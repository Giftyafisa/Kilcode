from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class NotificationBase(BaseModel):
    user_id: int
    title: str
    message: str
    type: str
    notification_data: Optional[Dict[str, Any]] = None
    read: bool = False

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True 