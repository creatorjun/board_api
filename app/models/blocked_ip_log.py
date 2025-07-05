from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.db.base_class import Base

class BlockedIpLog(Base):
    __tablename__ = "blocked_ip_logs"

    id = Column(Integer, primary_key=True, index=True)
    advertiser_id = Column(Integer, ForeignKey("advertisers.id"), nullable=False, index=True)
    ip_address = Column(String(255), nullable=False, index=True)
    memo = Column(String(255))
    blocked_at = Column(DateTime, server_default=func.now())