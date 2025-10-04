# DailyDevQ 백엔드 전용 Makefile

.PHONY: help setup up down restart logs build clean test

help: ## 사용 가능한 명령어 목록 표시
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## 초기 환경 설정 (.env 파일 생성)
	@echo "🔧 백엔드 환경 설정 중..."
	@if [ ! -f .env.local ]; then cp .env.example .env.local && echo "✅ .env.local 생성됨"; fi
	@echo "✅ 백엔드 환경 설정 완료!"

up: ## 백엔드 서비스 시작
	@echo "🚀 백엔드 서비스 시작 중..."
	docker-compose up -d
	@echo "✅ 백엔드가 시작되었습니다!"
	@echo "백엔드 API: http://localhost:8000"
	@echo "API 문서: http://localhost:8000/docs"
	@echo "MailHog: http://localhost:8025"

up-build: ## 백엔드 빌드 후 시작
	@echo "🔨 백엔드 빌드 및 시작 중..."
	docker-compose up --build -d
	@echo "✅ 백엔드가 빌드되고 시작되었습니다!"

down: ## 백엔드 서비스 중지
	@echo "⏹️  백엔드 서비스 중지 중..."
	docker-compose down
	@echo "✅ 백엔드 서비스가 중지되었습니다!"

down-v: ## 백엔드 서비스 중지 및 볼륨 삭제
	@echo "⏹️  백엔드 서비스 중지 및 볼륨 삭제 중..."
	docker-compose down -v
	@echo "✅ 백엔드 서비스가 중지되고 볼륨이 삭제되었습니다!"

restart: ## 백엔드 서비스 재시작
	@echo "🔄 백엔드 서비스 재시작 중..."
	docker-compose restart backend
	@echo "✅ 백엔드 서비스가 재시작되었습니다!"

logs: ## 백엔드 로그 보기
	docker-compose logs -f backend

logs-all: ## 전체 로그 보기
	docker-compose logs -f

ps: ## 실행 중인 컨테이너 상태 확인
	docker-compose ps

build: ## 이미지 빌드 (캐시 사용)
	@echo "🔨 백엔드 이미지 빌드 중..."
	docker-compose build
	@echo "✅ 이미지 빌드 완료!"

build-no-cache: ## 이미지 빌드 (캐시 미사용)
	@echo "🔨 백엔드 이미지 빌드 중 (캐시 미사용)..."
	docker-compose build --no-cache
	@echo "✅ 이미지 빌드 완료!"

shell: ## 백엔드 컨테이너 쉘 접속
	docker-compose exec backend sh

shell-postgres: ## PostgreSQL 접속
	docker-compose exec postgres psql -U dailydevq -d dailydevq

shell-redis: ## Redis CLI 접속
	docker-compose exec redis redis-cli -a redis123

test: ## 백엔드 테스트 실행
	docker-compose exec backend uv run pytest

test-cov: ## 백엔드 테스트 (커버리지 포함)
	docker-compose exec backend uv run pytest --cov=dailydevq_backend --cov-report=html

lint: ## Ruff로 린트 실행
	docker-compose exec backend uv run ruff check .

format: ## Ruff로 코드 포맷팅
	docker-compose exec backend uv run ruff format .

type-check: ## Mypy로 타입 체크
	docker-compose exec backend uv run mypy dailydevq_backend

install: ## 패키지 설치
	docker-compose exec backend uv pip install -e ".[dev]"

db-migrate: ## 데이터베이스 마이그레이션 실행
	docker-compose exec backend uv run alembic upgrade head

db-migrate-create: ## 새 마이그레이션 생성
	@read -p "마이그레이션 메시지를 입력하세요: " msg; \
	docker-compose exec backend uv run alembic revision --autogenerate -m "$$msg"

db-reset: ## 데이터베이스 초기화
	docker-compose down -v postgres
	docker-compose up -d postgres
	@echo "⏳ PostgreSQL 시작 대기 중..."
	sleep 5

clean: ## 중지된 컨테이너 및 미사용 이미지 정리
	@echo "🧹 정리 중..."
	docker-compose down
	docker system prune -f
	@echo "✅ 정리 완료!"

health: ## 서비스 헬스체크 상태 확인
	@echo "🏥 백엔드 상태 확인 중..."
	@docker inspect --format='Backend: {{.State.Health.Status}}' dailydevq-backend 2>/dev/null || echo "Backend: not running"
	@docker inspect --format='PostgreSQL: {{.State.Health.Status}}' dailydevq-postgres 2>/dev/null || echo "PostgreSQL: not running"
	@docker inspect --format='Redis: {{.State.Health.Status}}' dailydevq-redis 2>/dev/null || echo "Redis: not running"

stats: ## 컨테이너 리소스 사용량 확인
	docker stats dailydevq-backend dailydevq-postgres dailydevq-redis

.DEFAULT_GOAL := help
