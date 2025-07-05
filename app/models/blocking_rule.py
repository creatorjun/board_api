from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import DateTime

from app.db.base_class import Base

class BlockingRule(Base):
    __tablename__ = "blocking_rules"

    id = Column(Integer, primary_key=True, index=True)
    advertiser_id = Column(Integer, ForeignKey("advertisers.id"), nullable=False)
    name = Column(String(255), nullable=False)
    time_window_minutes = Column(Integer, nullable=False, default=60)
    max_clicks = Column(Integer, nullable=False, default=5)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())