from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import DateTime

from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    
    # 소셜 로그인 정보
    social_provider = Column(String(50), nullable=False) # 예: "naver", "kakao"
    social_id = Column(String(255), nullable=False) # 소셜 플랫폼에서 제공하는 고유 ID

    # 사용자 정보 (소셜 플랫폼에서 가져올 수 있는 부가 정보)
    nickname = Column(String(255))
    profile_image_url = Column(String(2048))
    
    is_active = Column(Boolean(), default=True)
    
    # 사용자와 광고주 관계
    advertiser_id = Column(Integer, ForeignKey("advertisers.id"))
    advertiser = relationship("Advertiser")
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('social_provider', 'social_id', name='_social_provider_uc'),
    )