from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.db.session import async_engine
from app.db.base_class import Base
# 우리가 만든 모든 라우터들을 import 합니다.
from app.apis import router_auth, router_ads, router_blocking_rules, router_blocked_ips, router_users

# FastAPI 앱의 시작과 종료 시점에 실행될 로직을 관리하는 lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # DB 테이블 생성을 위한 함수를 lifespan 내부로 이동
    async def create_tables():
        async with async_engine.begin() as conn:
            # Base.metadata.drop_all(conn) # 개발 중 테이블 구조 변경 시, 기존 테이블 삭제 후 재생성할 때 주석 해제
            await conn.run_sync(Base.metadata.create_all)

    # 앱 시작 시
    print("애플리케이션 시작")
    await create_tables()
    print("DB 테이블 생성 또는 확인 완료")
    yield
    # 앱 종료 시
    print("애플리케이션 종료")


# FastAPI 인스턴스 생성 시 lifespan 적용
app = FastAPI(
    title="부정클릭 방지 솔루션 API",
    description="네이버/카카오 소셜 로그인 및 네이버 광고 부정클릭 방지 기능을 제공합니다.",
    version="0.1.0",
    lifespan=lifespan
)

# --- 라우터들을 메인 앱에 모두 포함 ---
app.include_router(router_auth.router)
app.include_router(router_users.router)
app.include_router(router_ads.router)
app.include_router(router_blocked_ips.router)
app.include_router(router_blocking_rules.router)


# 루트 경로 API (서버 상태 확인용)
@app.get("/")
def read_root():
    return {"message": "Welcome to Fraud Detection Solution API"}