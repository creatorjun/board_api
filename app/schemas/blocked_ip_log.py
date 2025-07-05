from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BlockedIpLogRead(BaseModel):
    id: int
    ip_address: str
    memo: Optional[str]
    blocked_at: datetime

    class Config:
        from_attributes = True