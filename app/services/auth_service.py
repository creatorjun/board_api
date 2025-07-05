import httpx
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import User

NAVER_PROFILE_URL = "https://openapi.naver.com/v1/nid/me"
KAKAO_PROFILE_URL = "https://kapi.kakao.com/v2/user/me"

async def get_user_profile_from_social(provider: str, token: str):
    """
    소셜 플랫폼으로부터 사용자 프로필 정보를 가져옵니다.
    """
    headers = {"Authorization": f"Bearer {token}"}
    url = ""
    if provider == "naver":
        url = NAVER_PROFILE_URL
    elif provider == "kakao":
        url = KAKAO_PROFILE_URL
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported social provider"
        )

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            if provider == "naver":
                return response.json()["response"]
            elif provider == "kakao":
                profile_data = response.json()
                # Kakao API는 프로필 정보를 'properties'와 'kakao_account'에 나누어 제공
                return {
                    "id": profile_data["id"],
                    "nickname": profile_data["properties"].get("nickname"),
                    "profile_image_url": profile_data["properties"].get("profile_image"),
                }

        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Failed to fetch user profile from {provider}: {e.response.text}"
            )

async def get_or_create_user(db: AsyncSession, provider: str, user_profile: dict):
    """
    소셜 프로필 정보로 사용자를 찾거나 새로 생성합니다.
    """
    social_id = str(user_profile["id"])

    # 1. 기존 사용자인지 확인
    query = select(User).where(User.social_provider == provider, User.social_id == social_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user:
        return user

    # 2. 신규 사용자인 경우 새로 생성
    new_user = User(
        social_provider=provider,
        social_id=social_id,
        nickname=user_profile.get("nickname") or user_profile.get("name"), # Naver는 'name'으로 옴
        profile_image_url=user_profile.get("profile_image_url") or user_profile.get("profile_image") # Naver는 'profile_image'
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user