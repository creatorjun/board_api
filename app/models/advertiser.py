from sqlalchemy import Column, Integer, String, Boolean, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import DateTime

from app.db.base_class import Base

class Advertiser(Base):
    __tablename__ = "advertisers"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False)
    naver_customer_id = Column(BigInteger, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())