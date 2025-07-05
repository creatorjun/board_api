from fastapi import APIRouter, Request, Depends, BackgroundTasks, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from datetime import date

from app.db.session import get_db
from app.schemas.ad_click import AdClickData, AdClickRead
from app.services import fraud_detection_service
from app.models.advertiser import Advertiser
from app.models.ad_click import AdClick
from app.models.user import User
from app.core.security import get_current_user

router = APIRouter(
    prefix="/ads",
    tags=["Advertisement Tracking"]
)

@router.get("/landing/{advertiser_id}", include_in_schema=False)
async def track_ad_click(
    advertiser_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    ad_click_data: AdClickData = Depends(),
    db: AsyncSession = Depends(get_db)
):
    # 이 API는 외부(네이버)에서 호출되므로 JWT 인증을 적용하지 않습니다.
    query = select(Advertiser).where(Advertiser.id == advertiser_id)
    result = await db.execute(query)
    advertiser = result.scalar_one_or_none()

    if not advertiser or not advertiser.is_active:
        raise HTTPException(status_code=404, detail="Advertiser not found or not active")

    if advertiser.naver_customer_id != ad_click_data.customer_id:
        raise HTTPException(status_code=400, detail="Invalid customer ID for this tracking link")

    client_ip = request.client.host
    
    background_tasks.add_task(
        fraud_detection_service.process_ad_click,
        db,
        client_ip,
        advertiser,
        ad_click_data
    )
    
    return RedirectResponse(url=str(ad_click_data.destination_url))

@router.get("/clicks", response_model=List[AdClickRead])
async def get_ad_clicks_for_advertiser(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    로그인된 사용자의 광고주 계정에 대한 광고 클릭 로그 목록을 조회합니다.
    """
    if not current_user.advertiser_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not linked to an advertiser."
        )

    advertiser_id = current_user.advertiser_id
    query = select(AdClick).where(AdClick.advertiser_id == advertiser_id)

    if start_date:
        query = query.where(AdClick.created_at >= start_date)
    if end_date:
        query = query.where(AdClick.created_at <= end_date)
        
    query = query.order_by(AdClick.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    clicks = result.scalars().all()
    return clicks