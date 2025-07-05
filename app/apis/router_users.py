from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.advertiser import Advertiser
from app.schemas.user import UserRead
from app.schemas.advertiser import AdvertiserCreate

router = APIRouter()

@router.get("/users/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    현재 로그인된 사용자의 정보를 조회합니다.
    """
    return current_user

@router.put("/users/me/advertiser", response_model=UserRead)
async def link_user_to_advertiser(
    advertiser_in: AdvertiserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    현재 로그인된 사용자를 신규 광고주 정보와 연결합니다.
    사용자당 하나의 광고주만 연결할 수 있습니다.
    """
    if current_user.advertiser_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already linked to an advertiser."
        )

    # 이미 등록된 네이버 고객 ID인지 확인 (선택적: 정책에 따라 중복 허용 가능)
    existing_advertiser = await db.execute(
        select(Advertiser).where(Advertiser.naver_customer_id == advertiser_in.naver_customer_id)
    )
    if existing_advertiser.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An advertiser with this Naver Customer ID already exists."
        )

    # 새 광고주 생성
    new_advertiser = Advertiser(
        company_name=advertiser_in.company_name,
        naver_customer_id=advertiser_in.naver_customer_id
    )
    db.add(new_advertiser)
    await db.commit()
    await db.refresh(new_advertiser)

    # 현재 사용자와 새 광고주 연결
    current_user.advertiser_id = new_advertiser.id
    await db.commit()
    await db.refresh(current_user)
    
    return current_user