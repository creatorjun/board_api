from pydantic import BaseModel
from typing import Optional

class UserRead(BaseModel):
    id: int
    nickname: Optional[str] = None
    profile_image_url: Optional[str] = None
    social_provider: str
    advertiser_id: Optional[int] = None

    class Config:
        from_attributes = True