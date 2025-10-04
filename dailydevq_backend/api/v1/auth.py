"""
인증 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException
from dailydevq_backend.schemas.user import (
    GoogleAuthRequest,
    GoogleAuthResponse,
    UserCreate,
    UserResponse,
    AuthProvider,
)
from dailydevq_backend.services.user_service import user_service
from dailydevq_backend.services.google_oauth import google_oauth_service
from dailydevq_backend.utils.jwt import create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/google", response_model=GoogleAuthResponse)
async def google_auth(request: GoogleAuthRequest):
    """구글 OAuth 인증"""
    try:
        # 1. Google OAuth로 사용자 정보 가져오기
        google_user_info = await google_oauth_service.verify_and_get_user_info(
            request.code, request.redirect_uri
        )

        if not google_user_info:
            raise HTTPException(
                status_code=400, detail="Google 인증에 실패했습니다. 코드가 유효하지 않습니다."
            )

        # 2. 사용자 생성 또는 기존 사용자 조회
        user_data = UserCreate(
            email=google_user_info["email"],
            auth_provider=AuthProvider.GOOGLE,
            google_id=google_user_info["id"],
            name=google_user_info.get("name"),
            profile_image=google_user_info.get("picture"),
        )

        user = await user_service.create_user(user_data)

        # 3. JWT Access Token 생성
        access_token = create_access_token(user.id)

        # 4. 응답 반환
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

        return GoogleAuthResponse(
            success=True,
            message="Google 로그인에 성공했습니다",
            user=user_response,
            access_token=access_token,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google 인증 중 오류가 발생했습니다: {str(e)}")
