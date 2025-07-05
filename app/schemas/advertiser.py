from pydantic import BaseModel
from typing import Optional

class AdvertiserCreate(BaseModel):
    company_name: str
    naver_customer_id: int

class AdvertiserRead(BaseModel):
    id: int
    company_name: str
    naver_customer_id: int

    class Config:
        from_attributes = True