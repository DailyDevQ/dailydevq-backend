"""
애플리케이션 설정
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # 기본 설정
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    BACKEND_PORT: int = 8001

    # CORS 설정
    CORS_ORIGINS: str = "http://localhost:3000"

    # PostgreSQL 설정
    DATABASE_URL: str = "postgresql://dailydevq:dailydevq123@postgres:5432/dailydevq"

    # Redis 설정
    REDIS_URL: str = "redis://:redis123@redis:6379/0"

    # AWS 설정
    AWS_REGION: str = "ap-northeast-2"
    AWS_ACCESS_KEY_ID: str = "test"
    AWS_SECRET_ACCESS_KEY: str = "test"
    AWS_ENDPOINT_URL: Optional[str] = "http://localstack:4566"

    # DynamoDB 설정
    DYNAMODB_ENDPOINT: Optional[str] = "http://dynamodb-local:8000"  # 프로덕션에서는 None
    DYNAMODB_TABLE_PREFIX: str = "dailydevq-dev"
    DYNAMODB_USERS_TABLE: str = "users"

    # S3 설정
    S3_BUCKET_NAME: str = "dailydevq-dev-bucket"
    S3_ENDPOINT: Optional[str] = "http://localstack:4566"  # 프로덕션에서는 None

    # JWT 설정
    JWT_SECRET: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24

    # API 문서 설정
    ENABLE_SWAGGER: bool = True
    ENABLE_REDOC: bool = True

    # OpenAI 설정
    OPENAI_API_KEY: Optional[str] = None

    # Anthropic 설정
    ANTHROPIC_API_KEY: Optional[str] = None

    # Google OAuth 설정
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:3000/auth/google/callback"

    # Email 설정
    SMTP_HOST: str = "mailhog"
    SMTP_PORT: int = 1025
    SMTP_FROM: str = "noreply@dailydevq.dev"

    class Config:
        env_file = ".env.local"
        case_sensitive = True


settings = Settings()
