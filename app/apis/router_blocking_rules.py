from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.db.session import get_db
from app.models.blocking_rule import BlockingRule
from app.models.user import User
from app.schemas.blocking_rule import BlockingRuleCreate, BlockingRuleRead, BlockingRuleUpdate
from app.core.security import get_current_user

router = APIRouter(
    prefix="/blocking-rules",
    tags=["Blocking Rules"]
)

def check_user_advertiser_link(current_user: User):
    """사용자가 광고주에 연결되어 있는지 확인하는 헬퍼 함수"""
    if not current_user.advertiser_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not linked to an advertiser. Please link advertiser first."
        )
    return current_user.advertiser_id

@router.post("/", response_model=BlockingRuleRead, status_code=status.HTTP_201_CREATED)
async def create_blocking_rule_for_advertiser(
    rule_in: BlockingRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    로그인된 사용자의 광고주 계정에 새 차단 규칙을 생성합니다.
    """
    advertiser_id = check_user_advertiser_link(current_user)
    
    new_rule = BlockingRule(
        **rule_in.model_dump(),
        advertiser_id=advertiser_id
    )
    db.add(new_rule)
    await db.commit()
    await db.refresh(new_rule)
    return new_rule

@router.get("/", response_model=List[BlockingRuleRead])
async def get_blocking_rules_for_advertiser(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    로그인된 사용자의 광고주 계정에 속한 모든 차단 규칙 목록을 조회합니다.
    """
    advertiser_id = check_user_advertiser_link(current_user)

    query = select(BlockingRule).where(BlockingRule.advertiser_id == advertiser_id)
    result = await db.execute(query)
    rules = result.scalars().all()
    return rules

@router.put("/{rule_id}", response_model=BlockingRuleRead)
async def update_blocking_rule(
    rule_id: int,
    rule_in: BlockingRuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    로그인된 사용자의 광고주 계정에 속한 특정 차단 규칙을 수정합니다.
    """
    advertiser_id = check_user_advertiser_link(current_user)

    query = select(BlockingRule).where(BlockingRule.id == rule_id, BlockingRule.advertiser_id == advertiser_id)
    result = await db.execute(query)
    rule_to_update = result.scalar_one_or_none()

    if not rule_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blocking rule not found")

    update_data = rule_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(rule_to_update, key, value)
    
    await db.commit()
    await db.refresh(rule_to_update)
    return rule_to_update

@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blocking_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    로그인된 사용자의 광고주 계정에 속한 특정 차단 규칙을 삭제합니다.
    """
    advertiser_id = check_user_advertiser_link(current_user)

    query = select(BlockingRule).where(BlockingRule.id == rule_id, BlockingRule.advertiser_id == advertiser_id)
    result = await db.execute(query)
    rule_to_delete = result.scalar_one_or_none()

    if not rule_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blocking rule not found")
        
    await db.delete(rule_to_delete)
    await db.commit()
    return None