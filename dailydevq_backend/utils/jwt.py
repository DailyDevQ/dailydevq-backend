"""
JWT 토큰 생성 및 검증
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from dailydevq_backend.core.config import settings


def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT Access Token 생성
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRE_HOURS)

    to_encode = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
    }

    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    JWT Token 검증
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None
