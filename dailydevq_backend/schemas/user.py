"""
사용자 스키마
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class SubscriptionStatus(str, Enum):
    """구독 상태"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    UNSUBSCRIBED = "unsubscribed"


class AuthProvider(str, Enum):
    """인증 제공자"""
    EMAIL = "email"
    GOOGLE = "google"


class UserBase(BaseModel):
    """사용자 기본 스키마"""
    email: EmailStr


class UserCreate(UserBase):
    """사용자 생성 스키마"""
    auth_provider: AuthProvider = AuthProvider.EMAIL
    google_id: Optional[str] = None
    name: Optional[str] = None
    profile_image: Optional[str] = None


class UserResponse(UserBase):
    """사용자 응답 스키마"""
    id: str
    auth_provider: AuthProvider
    subscription_status: SubscriptionStatus
    name: Optional[str] = None
    profile_image: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SubscribeRequest(BaseModel):
    """구독 요청 스키마"""
    email: EmailStr


class SubscribeResponse(BaseModel):
    """구독 응답 스키마"""
    success: bool
    message: str
    user: Optional[UserResponse] = None


class GoogleAuthRequest(BaseModel):
    """구글 인증 요청 스키마"""
    code: str
    redirect_uri: str = Field(default="http://localhost:3000/auth/google/callback")


class GoogleAuthResponse(BaseModel):
    """구글 인증 응답 스키마"""
    success: bool
    message: str
    user: Optional[UserResponse] = None
    access_token: Optional[str] = None
