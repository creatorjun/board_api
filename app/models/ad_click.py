from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import DateTime

from app.db.base_class import Base

class AdClick(Base):
    __tablename__ = "ad_clicks"

    id = Column(Integer, primary_key=True, index=True)
    advertiser_id = Column(Integer, ForeignKey("advertisers.id"), nullable=False)
    client_ip = Column(String(255))
    destination_url = Column(String(2048))
    keyword = Column(String(255))
    match_type = Column(String(50))
    network_type = Column(String(50))
    device_type = Column(String(50))
    ad_group_id = Column(BigInteger)
    ad_id = Column(BigInteger)
    keyword_id = Column(BigInteger)
    creative_id = Column(BigInteger)
    query = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())