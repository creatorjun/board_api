from fastapi import APIRouter, Depends, Body, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services import auth_service
from app.core import security
from app.schemas.token import Token, SocialToken
from app.models.user import User

router = APIRouter()

@router.post("/login/{provider}", response_model=Token, tags=["Authentication"])
async def login_with_social_provider(
    provider: str,
    social_token: SocialToken = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    네이버 또는 카카오 소셜 로그인을 처리합니다.
    - 클라이언트로부터 소셜 플랫폼의 액세스 토큰을 받아 처리합니다.
    - 성공 시, 우리 시스템의 액세스 토큰과 리프레시 토큰을 반환합니다.
    """
    user_profile = await auth_service.get_user_profile_from_social(
        provider=provider,
        token=social_token.token
    )
    user = await auth_service.get_or_create_user(
        db=db,
        provider=provider,
        user_profile=user_profile
    )
    access_token = security.create_access_token(data={"sub": str(user.id)})
    refresh_token = security.create_refresh_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

# --- 테스트용 임시 API 수정 ---
@router.get("/test-token/{user_id}", response_model=Token, tags=["Authentication (Test)"])
async def get_test_token(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    (주의: 개발 및 테스트용) 지정된 user_id로 토큰을 즉시 발급합니다.
    """
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    access_token = security.create_access_token(data={"sub": str(user.id)})
    refresh_token = security.create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }