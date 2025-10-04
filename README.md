# DailyDevQ Backend

AI 기반 기술 면접 준비 서비스의 FastAPI 백엔드 API 서버

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# .env 파일 생성
make setup
```

### 2. Docker Compose로 실행

```bash
# 전체 백엔드 스택 시작 (PostgreSQL, Redis, DynamoDB, LocalStack 포함)
make up-build

# 또는
docker-compose up --build -d
```

### 3. API 접근

- **API 서버**: http://localhost:8000
- **API 문서 (Swagger)**: http://localhost:8000/docs
- **API 문서 (ReDoc)**: http://localhost:8000/redoc
- **MailHog (이메일 테스트)**: http://localhost:8025

## 📦 포함된 서비스

| 서비스 | 포트 | 설명 |
|--------|------|------|
| FastAPI Backend | 8000 | API 서버 |
| PostgreSQL | 5432 | 메인 데이터베이스 |
| Redis | 6379 | 캐시 서버 |
| DynamoDB Local | 8000 | NoSQL (AWS 개발용) |
| LocalStack | 4566 | AWS 서비스 에뮬레이션 |
| MailHog | 8025 | 이메일 테스트 UI |

## 🛠️ 개발 명령어

```bash
# 도움말
make help

# 서비스 관리
make up              # 서비스 시작
make down            # 서비스 중지
make restart         # 서비스 재시작
make logs            # 로그 보기

# 개발 도구
make shell           # 백엔드 컨테이너 접속
make test            # 테스트 실행
make test-cov        # 테스트 (커버리지)
make lint            # 린트 실행
make format          # 코드 포맷팅
make type-check      # 타입 체크

# 데이터베이스
make db-migrate      # 마이그레이션 실행
make db-reset        # DB 초기화
```

## 📁 프로젝트 구조

```
dailydevq-backend/
├── dailydevq_backend/     # 메인 애플리케이션
│   ├── __init__.py
│   ├── main.py            # FastAPI 앱
│   ├── api/               # API 라우터
│   ├── core/              # 핵심 설정
│   ├── models/            # 데이터 모델
│   ├── schemas/           # Pydantic 스키마
│   ├── services/          # 비즈니스 로직
│   └── utils/             # 유틸리티
├── tests/                 # 테스트
├── alembic/               # DB 마이그레이션
├── docker-compose.yml     # Docker 설정
├── Dockerfile.dev         # 개발용 Dockerfile
├── pyproject.toml         # Python 프로젝트 설정
├── Makefile               # 편의 명령어
└── README.md
```

## 🔗 프론트엔드 연동

프론트엔드는 별도 레포에서 관리됩니다:
- **레포**: `dailydevq-app`
- **URL**: http://localhost:3000

두 서비스는 `dailydevq-shared` Docker 네트워크로 연결됩니다.

## 🧪 테스트

```bash
# 전체 테스트
make test

# 커버리지 포함
make test-cov

# 특정 테스트만
docker-compose exec backend uv run pytest tests/test_main.py
```

## 📝 API 개발

1. `dailydevq_backend/api/` 에 라우터 추가
2. `dailydevq_backend/main.py` 에 라우터 등록
3. 테스트 작성
4. API 문서 자동 생성됨

## 🔐 환경 변수

`.env.example` 참조하여 `.env.local` 생성

주요 환경 변수:
- `DATABASE_URL`: PostgreSQL 연결 URL
- `REDIS_URL`: Redis 연결 URL
- `JWT_SECRET`: JWT 시크릿 키
- `OPENAI_API_KEY`: OpenAI API 키
- `ANTHROPIC_API_KEY`: Anthropic API 키

## 🚢 배포

프로덕션 배포는 `dailydevq-infra` 레포의 Terraform으로 관리됩니다.

## 📚 기술 스택

- **Framework**: FastAPI 0.115+
- **Language**: Python 3.12+
- **Package Manager**: uv
- **Database**: PostgreSQL 16
- **Cache**: Redis 7
- **ORM**: SQLAlchemy 2.0
- **Migration**: Alembic
- **Testing**: pytest
- **Linting**: Ruff
- **Type Checking**: Mypy

## 🤝 기여

1. 브랜치 생성
2. 변경 사항 커밋
3. 테스트 실행
4. PR 생성

## 📄 라이선스

MIT License
