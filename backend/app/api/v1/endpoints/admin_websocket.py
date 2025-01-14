from fastapi import APIRouter, WebSocket, Depends, HTTPException
from app.core.websocket_manager import manager
from app.api import deps
from app.models.admin import Admin
from typing import Optional
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/ws/admin/{country}")
async def admin_websocket(
    websocket: WebSocket,
    country: str,
    token: Optional[str] = None,
):
    try:
        # Validate admin token and country
        admin = await deps.get_current_admin_ws(token)
        if not admin or admin.country.lower() != country.lower():
            await websocket.close(code=4003)
            return

        # Connect admin to their country's WebSocket
        await manager.connect_admin(websocket, country.lower())
        
        try:
            while True:
                # Keep connection alive and handle messages
                data = await websocket.receive_json()
                logger.debug(f"Received message from {country} admin: {data}")
                
                # Handle admin acknowledgments
                if data.get("type") == "ACK":
                    logger.info(f"Admin {admin.id} acknowledged message: {data.get('message_id')}")
                
        except Exception as e:
            logger.error(f"WebSocket error for admin {admin.id}: {str(e)}")
            
    except Exception as e:
        logger.error(f"Failed to establish WebSocket connection: {str(e)}")
        await websocket.close(code=4000) 