from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class ActivityBase(BaseModel):
    user_id: int
    activity_type: str
    description: str
    activity_metadata: Optional[Dict[str, Any]] = None
    country: str
    status: str = "success"

class ActivityCreate(ActivityBase):
    pass

class Activity(ActivityBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True 