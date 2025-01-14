from fastapi import WebSocket
from typing import Dict, Set, Optional
import logging
import ssl
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.admin_connections: Dict[str, Set[WebSocket]] = {}
        self.user_connections: Dict[str, Dict[str, WebSocket]] = {}
        self.ssl_context = self._create_ssl_context()
        logger.info("WebSocket manager initialized")

    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context for secure WebSocket connections"""
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        try:
            context.load_cert_chain(
                certfile="fullchain.pem",
                keyfile="privkey.pem"
            )
            context.verify_mode = ssl.CERT_OPTIONAL
            context.check_hostname = False
            logger.info("SSL context created successfully")
            return context
        except Exception as e:
            logger.warning(f"Failed to create SSL context: {e}")
            return None

    async def connect(self, websocket: WebSocket, user_id: str, country: str):
        """Connect a regular user"""
        if country not in self.user_connections:
            self.user_connections[country] = {}
        self.user_connections[country][user_id] = websocket
        logger.info(f"User {user_id} connected from {country}")

    async def disconnect(self, websocket: WebSocket, user_id: str, country: str):
        """Disconnect a regular user"""
        if country in self.user_connections and user_id in self.user_connections[country]:
            del self.user_connections[country][user_id]
            logger.info(f"User {user_id} disconnected from {country}")

    async def connect_admin(self, websocket: WebSocket, country: str):
        """Connect an admin user"""
        if country not in self.admin_connections:
            self.admin_connections[country] = set()
        self.admin_connections[country].add(websocket)
        logger.info(f"Admin connected to {country}")

    async def disconnect_admin(self, websocket: WebSocket, country: str):
        """Disconnect an admin user"""
        if country in self.admin_connections:
            self.admin_connections[country].discard(websocket)
            logger.info(f"Admin disconnected from {country}")

    async def broadcast_to_country(self, message: str, country: str):
        """Broadcast message to all users in a country"""
        if country in self.user_connections:
            disconnected = []
            for user_id, websocket in self.user_connections[country].items():
                try:
                    await websocket.send_text(message)
                except Exception as e:
                    logger.error(f"Failed to send to user {user_id}: {e}")
                    disconnected.append((user_id, websocket))

            # Clean up disconnected users
            for user_id, _ in disconnected:
                del self.user_connections[country][user_id]

    async def broadcast_to_admins(self, message: str, country: str):
        """Broadcast message to all admins in a country"""
        if country in self.admin_connections:
            disconnected = set()
            for websocket in self.admin_connections[country]:
                try:
                    await websocket.send_text(message)
                except Exception as e:
                    logger.error(f"Failed to send to admin: {e}")
                    disconnected.add(websocket)

            # Clean up disconnected admins
            self.admin_connections[country] -= disconnected

    async def send_personal_message(self, message: str, user_id: str, country: str):
        """Send a message to a specific user"""
        if country in self.user_connections and user_id in self.user_connections[country]:
            try:
                await self.user_connections[country][user_id].send_text(message)
                logger.info(f"Sent personal message to user {user_id}")
            except Exception as e:
                logger.error(f"Failed to send personal message to user {user_id}: {e}")
                del self.user_connections[country][user_id] 

# Create a global instance of the connection manager
manager = ConnectionManager() 