from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.sync import SyncRequest, SyncResponse
from app.core.logger import logger
from app.core.database import get_db
from sqlalchemy.orm import Session
from datetime import datetime

router = APIRouter()

@router.post("/sync", response_model=SyncResponse)
async def sync_data(
    sync_request: SyncRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    authorization: str = Header(None)
):
    try:
        if not authorization or not authorization.startswith('Bearer '):
            raise HTTPException(
                status_code=401,
                detail="Invalid authorization header"
            )

        logger.debug(f"Sync request from user {current_user.email}")
        logger.debug(f"Last sync: {sync_request.lastSync}, Version: {sync_request.version}")

        # Convert lastSync to datetime if it's not None
        last_sync_date = datetime.fromisoformat(sync_request.lastSync) if sync_request.lastSync else None

        # Get updates since last sync
        updates = []

        # Check for betting code updates
        code_updates = await get_code_updates(
            current_user.id, 
            last_sync_date,
            db
        )
        updates.extend(code_updates)

        # Check for payment updates
        payment_updates = await get_payment_updates(
            current_user.id, 
            last_sync_date,
            db
        )
        updates.extend(payment_updates)

        # Check for user settings updates
        settings_updates = await get_settings_updates(
            current_user.id, 
            last_sync_date,
            db
        )
        updates.extend(settings_updates)

        # Generate new version
        new_version = str(int(sync_request.version) + 1)

        return SyncResponse(
            updates=updates,
            newVersion=new_version
        )

    except Exception as e:
        logger.error(f"Sync error for user {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to sync data"
        )

async def get_code_updates(user_id: int, last_sync: datetime, db: Session) -> list:
    # Implement fetching code updates since last_sync
    return []

async def get_payment_updates(user_id: int, last_sync: datetime, db: Session) -> list:
    # Implement fetching payment updates since last_sync
    return []

async def get_settings_updates(user_id: int, last_sync: datetime, db: Session) -> list:
    # Implement fetching settings updates since last_sync
    return [] 