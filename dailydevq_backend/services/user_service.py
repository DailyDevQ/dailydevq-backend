"""
사용자 서비스
"""

from typing import Optional
from botocore.exceptions import ClientError
from dailydevq_backend.core.database import dynamodb_client
from dailydevq_backend.core.config import settings
from dailydevq_backend.models.user import UserModel
from dailydevq_backend.schemas.user import UserCreate, AuthProvider, SubscriptionStatus


class UserService:
    """사용자 서비스"""

    def __init__(self):
        self.table = dynamodb_client.get_table(settings.DYNAMODB_USERS_TABLE)

    async def create_user(self, user_data: UserCreate) -> UserModel:
        """사용자 생성"""
        # 이메일 중복 체크
        existing_user = await self.get_user_by_email(user_data.email)
        if existing_user:
            # 이미 존재하는 경우 활성화 상태로 업데이트
            if existing_user.subscription_status == SubscriptionStatus.UNSUBSCRIBED.value:
                existing_user.subscription_status = SubscriptionStatus.ACTIVE.value
                await self.update_user(existing_user)
            return existing_user

        # 새 사용자 생성
        user = UserModel(
            email=user_data.email,
            auth_provider=user_data.auth_provider,
            google_id=user_data.google_id,
            name=user_data.name,
            profile_image=user_data.profile_image,
        )

        # DynamoDB에 저장
        try:
            self.table.put_item(Item=user.to_dict())
            return user
        except ClientError as e:
            raise Exception(f"Failed to create user: {str(e)}")

    async def get_user_by_id(self, user_id: str) -> Optional[UserModel]:
        """ID로 사용자 조회"""
        try:
            response = self.table.get_item(Key={"id": user_id})
            if "Item" in response:
                return UserModel.from_dict(response["Item"])
            return None
        except ClientError as e:
            raise Exception(f"Failed to get user by id: {str(e)}")

    async def get_user_by_email(self, email: str) -> Optional[UserModel]:
        """이메일로 사용자 조회"""
        try:
            response = self.table.query(
                IndexName="email-index",
                KeyConditionExpression="email = :email",
                ExpressionAttributeValues={":email": email},
            )
            if response["Items"]:
                return UserModel.from_dict(response["Items"][0])
            return None
        except ClientError as e:
            raise Exception(f"Failed to get user by email: {str(e)}")

    async def get_user_by_google_id(self, google_id: str) -> Optional[UserModel]:
        """Google ID로 사용자 조회"""
        try:
            response = self.table.query(
                IndexName="google-id-index",
                KeyConditionExpression="google_id = :google_id",
                ExpressionAttributeValues={":google_id": google_id},
            )
            if response["Items"]:
                return UserModel.from_dict(response["Items"][0])
            return None
        except ClientError:
            # google-id-index가 없으면 scan으로 조회 (비효율적이지만 fallback)
            response = self.table.scan(
                FilterExpression="google_id = :google_id",
                ExpressionAttributeValues={":google_id": google_id},
            )
            if response["Items"]:
                return UserModel.from_dict(response["Items"][0])
            return None

    async def update_user(self, user: UserModel) -> UserModel:
        """사용자 업데이트"""
        try:
            self.table.put_item(Item=user.to_dict())
            return user
        except ClientError as e:
            raise Exception(f"Failed to update user: {str(e)}")

    async def unsubscribe_user(self, email: str) -> bool:
        """구독 취소"""
        user = await self.get_user_by_email(email)
        if not user:
            return False

        user.subscription_status = SubscriptionStatus.UNSUBSCRIBED.value
        await self.update_user(user)
        return True


user_service = UserService()
