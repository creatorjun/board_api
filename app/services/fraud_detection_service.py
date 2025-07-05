from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta

from app.models.advertiser import Advertiser
from app.models.ad_click import AdClick
from app.models.blocking_rule import BlockingRule
from app.models.blocked_ip_log import BlockedIpLog
from app.schemas.ad_click import AdClickData
from app.services import naver_ad_service

async def process_ad_click(db: AsyncSession, client_ip: str, advertiser: Advertiser, ad_click_data: AdClickData):
    # ... 기존 클릭 로그 저장 로직 (변경 없음) ...
    new_click = AdClick(
        client_ip=client_ip,
        advertiser_id=advertiser.id,
        # ... 이하 생략 ...
        query=ad_click_data.query
    )
    db.add(new_click)
    await db.commit()

    # ... 기존 규칙 조회 및 클릭 수 계산 로직 (변경 없음) ...
    rule_query = select(BlockingRule).where(
        BlockingRule.advertiser_id == advertiser.id,
        BlockingRule.is_active
    )
    # ... 이하 생략 ...
    click_count = click_count_result.scalar_one()

    if click_count > blocking_rule.max_clicks:
        check_query = select(BlockedIpLog).where(
            BlockedIpLog.advertiser_id == advertiser.id,
            BlockedIpLog.ip_address == client_ip
        )
        check_result = await db.execute(check_query)
        already_blocked = check_result.scalar_one_or_none()
        
        if not already_blocked:
            # --- 여기부터 로직 변경 ---
            try:
                # 1. 우리 DB에 차단 로그를 '준비'만 합니다 (아직 저장 안 함).
                new_blocked_ip = BlockedIpLog(
                    advertiser_id=advertiser.id,
                    ip_address=client_ip,
                    memo="자동화 솔루션에 의해 차단됨"
                )
                db.add(new_blocked_ip)
                
                # 2. 네이버 광고 API를 호출합니다.
                await naver_ad_service.block_ip_address(
                    customer_id=advertiser.naver_customer_id,
                    ip_address=client_ip
                )
                
                # 3. API 호출이 성공했을 때만 DB에 최종 저장(commit)합니다.
                await db.commit()
                print(f"성공: IP {client_ip} 차단 및 DB 저장 완료. 광고주 ID: {advertiser.id}")

            except Exception as e:
                # 4. API 호출이 실패하면 DB 변경사항을 모두 취소(rollback)합니다.
                await db.rollback()
                print(f"실패: 네이버 API 연동 오류로 DB 롤백. IP: {client_ip}, 오류: {e}")