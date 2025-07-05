from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from datetime import datetime

# --- 기존 스키마 (수정 없음) ---
class AdClickData(BaseModel):
    destination_url: HttpUrl = Field(..., alias='final_url')
    customer_id: int = Field(..., alias='customerid')
    
    network_type: str = Field(..., alias='n_network')
    match_type: str = Field(..., alias='n_match')
    keyword: str = Field(..., alias='n_keyword')
    query: Optional[str] = Field(None, alias='n_query')
    device_type: str = Field(..., alias='n_media')
    
    ad_group_id: int = Field(..., alias='n_ad_group')
    ad_id: int = Field(..., alias='n_ad')
    keyword_id: int = Field(..., alias='n_keyword_id')
    creative_id: int = Field(..., alias='n_creative')

    class Config:
        populate_by_name = True
        from_attributes = True

# --- 새로 추가된 스키마 ---
class AdClickRead(BaseModel):
    id: int
    client_ip: str
    advertiser_id: int
    keyword: Optional[str]
    query: Optional[str]
    network_type: Optional[str]
    device_type: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True