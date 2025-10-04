"""
FastAPI 메인 애플리케이션
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dailydevq_backend.core.config import settings
from dailydevq_backend.api.v1 import subscribe, auth

app = FastAPI(
    title="DailyDevQ API",
    description="Tech Newsletter & Developer Community Platform",
    version="1.0.0",
    docs_url="/docs" if settings.ENABLE_SWAGGER else None,
    redoc_url="/redoc" if settings.ENABLE_REDOC else None,
)

# CORS 설정
cors_origins = settings.CORS_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(subscribe.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "service": "DailyDevQ API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {
        "status": "healthy",
        "service": "dailydevq-backend",
    }


@app.get("/api/v1/ping")
async def ping():
    """핑 엔드포인트"""
    return {"message": "pong"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "dailydevq_backend.main:app",
        host="0.0.0.0",
        port=settings.BACKEND_PORT,
        reload=True,
    )
