from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BlockingRuleBase(BaseModel):
    name: Optional[str] = None
    time_window_minutes: Optional[int] = 60
    max_clicks: Optional[int] = 5
    is_active: Optional[bool] = True

class BlockingRuleCreate(BlockingRuleBase):
    name: str
    time_window_minutes: int
    max_clicks: int

class BlockingRuleUpdate(BlockingRuleBase):
    pass

class BlockingRuleRead(BlockingRuleBase):
    id: int
    advertiser_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True