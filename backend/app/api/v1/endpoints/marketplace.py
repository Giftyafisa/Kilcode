from fastapi import APIRouter, HTTPException
from typing import Dict

router = APIRouter()

@router.get("/status")
async def get_marketplace_status() -> Dict:
    """Get the current status of the marketplace"""
    try:
        return {
            "status": "online",
            "features": {
                "payments": True,
                "notifications": True,
                "websocket": True
            },
            "version": "1.0.0"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 