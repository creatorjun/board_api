from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.db.session import get_db
from app.models.blocked_ip_log import BlockedIpLog
from app.models.user import User
from app.schemas.blocked_ip_log import BlockedIpLogRead
from app.core.security import get_current_user

router = APIRouter(
    prefix="/blocked-ips",
    tags=["Blocked IPs"]
)

@router.get("/", response_model=List[BlockedIpLogRead])
async def get_blocked_ips_for_advertiser(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    로그인된 사용자의 광고주 계정에서 차단된 IP 로그 목록을 조회합니다.
    """
    if not current_user.advertiser_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not linked to an advertiser."
        )

    advertiser_id = current_user.advertiser_id
    query = (
        select(BlockedIpLog)
        .where(BlockedIpLog.advertiser_id == advertiser_id)
        .order_by(BlockedIpLog.blocked_at.desc())
        .offset(skip)
        .limit(limit)
    )
    
    result = await db.execute(query)
    blocked_ips = result.scalars().all()
    return blocked_ips