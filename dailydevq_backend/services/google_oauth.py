"""
Google OAuth 서비스
"""

import httpx
from typing import Optional, Dict, Any
from dailydevq_backend.core.config import settings


class GoogleOAuthService:
    """Google OAuth 인증 서비스"""

    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """
        Authorization code를 access token으로 교환
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.GOOGLE_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
            )

            if response.status_code != 200:
                raise Exception(f"Failed to exchange code for token: {response.text}")

            return response.json()

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Access token으로 사용자 정보 가져오기
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if response.status_code != 200:
                raise Exception(f"Failed to get user info: {response.text}")

            return response.json()

    async def verify_and_get_user_info(
        self, code: str, redirect_uri: str
    ) -> Optional[Dict[str, Any]]:
        """
        Authorization code 검증 및 사용자 정보 반환
        """
        try:
            # 1. Code를 Token으로 교환
            token_data = await self.exchange_code_for_token(code, redirect_uri)
            access_token = token_data.get("access_token")

            if not access_token:
                return None

            # 2. Token으로 사용자 정보 가져오기
            user_info = await self.get_user_info(access_token)

            return {
                "id": user_info.get("id"),
                "email": user_info.get("email"),
                "name": user_info.get("name"),
                "picture": user_info.get("picture"),
                "verified_email": user_info.get("verified_email", False),
            }

        except Exception as e:
            print(f"Google OAuth Error: {str(e)}")
            return None


google_oauth_service = GoogleOAuthService()
