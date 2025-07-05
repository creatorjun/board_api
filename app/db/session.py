from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings

# 비동기 DB 엔진 생성
# pool_pre_ping=True 옵션은 커넥션 풀에서 연결을 가져올 때,
# 연결이 유효한지(예: DB서버가 재시작되지 않았는지) 미리 테스트하는 기능입니다.
async_engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)

# 비동기 세션 생성을 위한 세션메이커
# autocommit=False, autoflush=False 는 SQLAlchemy 2.0의 표준 권장사항입니다.
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
)

# API 요청마다 DB 세션을 생성하고, 요청이 끝나면 닫는 의존성 함수
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()