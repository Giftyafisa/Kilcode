from fastapi import APIRouter, Depends
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/health")
async def health_check(current_user: User = Depends(get_current_user)):
    """
    Health check endpoint for WebSocket fallback
    """
    return {"status": "healthy", "user_id": current_user.id}

@router.get("/updates")
async def get_updates(current_user: User = Depends(get_current_user)):
    """
    Polling endpoint for when WebSocket is unavailable
    """
    # You can implement logic to fetch pending updates for the user
    return {
        "updates": []  # Return any pending updates from your database
    } 