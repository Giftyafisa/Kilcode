from typing import Dict, Any, Optional
from fastapi import WebSocket
import logging
from .websocket_manager import manager
from datetime import datetime

logger = logging.getLogger(__name__)

class NotificationManager:
    def __init__(self):
        self.ws_manager = manager
        logger.info("Notification Manager initialized")

    async def notify_betting_code_submission(
        self,
        country: str,
        betting_code: Dict[str, Any]
    ):
        """Notify admins when a new betting code is submitted"""
        try:
            message = {
                "type": "NEW_BETTING_CODE",
                "data": {
                    "id": betting_code["id"],
                    "user_name": betting_code["user_name"],
                    "bookmaker": betting_code["bookmaker"],
                    "code": betting_code["code"],
                    "odds": betting_code["odds"],
                    "stake": betting_code["stake"],
                    "potential_winnings": betting_code["potential_winnings"],
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            await self.ws_manager.broadcast_to_country_admins(country.lower(), message)
            logger.info(f"Betting code notification sent to {country} admins")
        except Exception as e:
            logger.error(f"Failed to send betting code notification: {str(e)}")

    async def notify_code_verification(
        self,
        user_id: int,
        code_id: int,
        status: str,
        winnings: Optional[float] = None,
        note: Optional[str] = None
    ):
        """Notify user when their betting code is verified"""
        try:
            message = {
                "type": "BETTING_CODE_VERIFIED",
                "data": {
                    "code_id": code_id,
                    "status": status,
                    "message": f"Your betting code has been marked as {status}",
                    "winnings": winnings if status == "won" else 0,
                    "admin_note": note,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            # Send to specific user
            await self.ws_manager.send_to_user(user_id, message)
            logger.info(f"Verification notification sent to user {user_id}")
        except Exception as e:
            logger.error(f"Failed to send verification notification: {str(e)}")

    async def notify_admin_action(
        self,
        country: str,
        action_type: str,
        data: Dict[str, Any]
    ):
        """Notify other admins of admin actions"""
        try:
            message = {
                "type": f"ADMIN_{action_type}",
                "data": {
                    **data,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            await self.ws_manager.broadcast_to_country_admins(country.lower(), message)
            logger.info(f"Admin action notification sent to {country} admins")
        except Exception as e:
            logger.error(f"Failed to send admin action notification: {str(e)}")

    async def notify_system_error(
        self,
        country: str,
        error_type: str,
        error_message: str
    ):
        """Notify admins of system errors"""
        try:
            message = {
                "type": "SYSTEM_ERROR",
                "data": {
                    "error_type": error_type,
                    "message": error_message,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            await self.ws_manager.broadcast_to_country_admins(country.lower(), message)
            logger.error(f"System error notification sent: {error_message}")
        except Exception as e:
            logger.error(f"Failed to send error notification: {str(e)}")

notification_manager = NotificationManager() 