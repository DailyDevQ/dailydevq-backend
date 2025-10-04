"""
FastAPI 메인 애플리케이션
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="DailyDevQ API",
    description="AI-powered technical interview preparation service",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENABLE_SWAGGER", "true").lower() == "true" else None,
    redoc_url="/redoc" if os.getenv("ENABLE_REDOC", "true").lower() == "true" else None,
)

# CORS 설정
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
        port=int(os.getenv("BACKEND_PORT", "8000")),
        reload=True,
    )
