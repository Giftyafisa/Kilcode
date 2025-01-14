from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class SyncRequest(BaseModel):
    lastSync: str
    version: str

class SyncResponse(BaseModel):
    updates: List[Dict[str, Any]]
    newVersion: str 