"""
사용자 모델 (DynamoDB)
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4
from dailydevq_backend.schemas.user import AuthProvider, SubscriptionStatus


class UserModel:
    """DynamoDB 사용자 모델"""

    def __init__(
        self,
        email: str,
        auth_provider: AuthProvider = AuthProvider.EMAIL,
        user_id: Optional[str] = None,
        google_id: Optional[str] = None,
        name: Optional[str] = None,
        profile_image: Optional[str] = None,
        subscription_status: SubscriptionStatus = SubscriptionStatus.ACTIVE,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = user_id or str(uuid4())
        self.email = email
        self.auth_provider = auth_provider.value if isinstance(auth_provider, AuthProvider) else auth_provider
        self.google_id = google_id
        self.name = name
        self.profile_image = profile_image
        self.subscription_status = subscription_status.value if isinstance(subscription_status, SubscriptionStatus) else subscription_status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self) -> dict:
        """DynamoDB 아이템으로 변환"""
        return {
            "id": self.id,
            "email": self.email,
            "auth_provider": self.auth_provider,
            "google_id": self.google_id,
            "name": self.name,
            "profile_image": self.profile_image,
            "subscription_status": self.subscription_status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UserModel":
        """DynamoDB 아이템에서 생성"""
        return cls(
            user_id=data.get("id"),
            email=data["email"],
            auth_provider=data.get("auth_provider", AuthProvider.EMAIL.value),
            google_id=data.get("google_id"),
            name=data.get("name"),
            profile_image=data.get("profile_image"),
            subscription_status=data.get("subscription_status", SubscriptionStatus.ACTIVE.value),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
        )

    def update(self, **kwargs):
        """모델 업데이트"""
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
