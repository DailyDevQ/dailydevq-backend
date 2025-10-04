# 프로덕션용 FastAPI Dockerfile (멀티스테이지 빌드)
FROM python:3.12-slim AS builder

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# uv 설치
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사
COPY pyproject.toml ./

# 가상환경 생성 및 의존성 설치
RUN uv venv && \
    uv pip install --no-cache-dir -e .

# 프로덕션 스테이지
FROM python:3.12-slim

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# 시스템 패키지 업데이트 및 필수 도구 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# 빌더 스테이지에서 가상환경 복사
COPY --from=builder /app/.venv /app/.venv

# 애플리케이션 코드 복사
COPY dailydevq_backend ./dailydevq_backend

# 비루트 사용자 생성 및 권한 설정
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 포트 노출
EXPOSE 8000

# 프로덕션 서버 실행 (Uvicorn with multiple workers)
CMD ["uvicorn", "dailydevq_backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
