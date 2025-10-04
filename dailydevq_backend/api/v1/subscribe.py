"""
구독 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException
from dailydevq_backend.schemas.user import (
    SubscribeRequest,
    SubscribeResponse,
    UserCreate,
    UserResponse,
    AuthProvider,
)
from dailydevq_backend.services.user_service import user_service

router = APIRouter(prefix="/subscribe", tags=["Subscribe"])


@router.post("/email", response_model=SubscribeResponse)
async def subscribe_with_email(request: SubscribeRequest):
    """이메일로 구독하기"""
    try:
        # 사용자 생성
        user_data = UserCreate(
            email=request.email,
            auth_provider=AuthProvider.EMAIL,
        )
        user = await user_service.create_user(user_data)

        # 응답 변환
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            auth_provider=AuthProvider(user.auth_provider),
            subscription_status=user.subscription_status,
            name=user.name,
            profile_image=user.profile_image,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

        return SubscribeResponse(
            success=True,
            message="구독이 완료되었습니다! 평일 오전 7시에 뉴스레터를 받아보실 수 있습니다.",
            user=user_response,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"구독 처리 중 오류가 발생했습니다: {str(e)}")


@router.delete("/unsubscribe")
async def unsubscribe(email: str):
    """구독 취소"""
    try:
        success = await user_service.unsubscribe_user(email)
        if not success:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

        return {
            "success": True,
            "message": "구독이 취소되었습니다",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"구독 취소 중 오류가 발생했습니다: {str(e)}")


@router.get("/status/{email}")
async def get_subscription_status(email: str):
    """구독 상태 확인"""
    try:
        user = await user_service.get_user_by_email(email)
        if not user:
            return {
                "subscribed": False,
                "message": "구독 정보를 찾을 수 없습니다",
            }

        return {
            "subscribed": user.subscription_status == "active",
            "status": user.subscription_status,
            "email": user.email,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"구독 상태 조회 중 오류가 발생했습니다: {str(e)}")
