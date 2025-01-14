from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, status
from app.core.auth import get_current_user_ws, get_current_admin_ws
from app.core.websocket_manager import ConnectionManager
from app.models.user import User
from app.models.admin import Admin
from typing import Optional
import logging
from jose import jwt, JWTError
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize WebSocket manager
manager = ConnectionManager()

@router.websocket("/ws/admin/{country}")
async def websocket_endpoint(websocket: WebSocket, country: str, token: Optional[str] = None):
    """WebSocket endpoint for real-time betting code updates"""
    try:
        # Authenticate admin before accepting connection
        admin = await get_current_admin_ws(token)
        if not admin:
            logger.warning("Invalid token or admin not found")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
            
        # Verify admin has access to requested country
        if admin.country.lower() != country.lower():
            logger.warning(f"Admin {admin.email} attempted to access unauthorized country: {country}")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
            
        # Accept connection only after successful authentication
        await websocket.accept()
        
        # Register connection with manager
        logger.info(f"Admin {admin.email} connected to country: {country}")
        await manager.connect_admin(websocket, country)
        
        try:
            while True:
                data = await websocket.receive_text()
                # Handle received data if needed
                
        except WebSocketDisconnect:
            logger.info(f"Admin {admin.email} disconnected from country: {country}")
            await manager.disconnect_admin(websocket, country)
                
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        if not websocket.client_state.DISCONNECTED:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)

@router.websocket("/ws")
async def user_websocket_endpoint(websocket: WebSocket, token: Optional[str] = None):
    """WebSocket endpoint for regular users"""
    try:
        # Extract country from query params
        params = dict(websocket.query_params)
        country = params.get('country', '').lower()
        
        # Validate token first
        user = await get_current_user_ws(token)
        if not user:
            logger.warning("Invalid token or user not found")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
            
        # Validate country
        user_country = user.country.lower() if user.country else None
        
        if not user_country:
            logger.warning(f"No country found for user {user.email}")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
            
        # Ensure provided country matches user's country
        if country != user_country:
            logger.warning(f"Country mismatch for user {user.email}: {country} != {user_country}")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
            
        if user_country not in ['ghana', 'nigeria']:
            logger.warning(f"Invalid country {user_country} for user {user.email}")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
                
        # Accept connection only after all validation passes
        await websocket.accept()
        logger.info(f"User {user.email} connected from country: {user_country}")
            
        # Connect user with country
        try:
            await manager.connect(websocket, f"{user.email}", user_country)
            
            while True:
                data = await websocket.receive_text()
                # Handle received data if needed
                
        except WebSocketDisconnect:
            logger.info(f"User {user.email} disconnected from {user_country}")
            await manager.disconnect(websocket, f"{user.email}", user_country)
                
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        if not websocket.client_state.DISCONNECTED:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR) 