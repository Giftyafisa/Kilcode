from pydantic_settings import BaseSettings
from typing import List, Optional
import secrets

class AdminSettings(BaseSettings):
    # Admin API settings
    ADMIN_API_PORT: int = 8001
    ADMIN_SECRET_KEY: str = secrets.token_urlsafe(32)
    ADMIN_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    ADMIN_DATABASE_URL: str = "sqlite:///./admin.db"
    
    # Main backend settings
    MAIN_BACKEND_URL: str = "http://localhost:8000"
    
    # API settings
    API_V1_STR: str = "/api/v1"
    
    # Environment settings
    ENVIRONMENT: str = "development"
    
    # Security settings
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # Payment settings (MTN)
    MTN_API_URL: Optional[str] = "https://sandbox.momodeveloper.mtn.com"
    MTN_SUBSCRIPTION_KEY: Optional[str] = None
    MTN_API_USER: Optional[str] = None
    MTN_API_KEY: Optional[str] = None
    
    # Websocket settings
    WS_URL: str = "ws://localhost:8000"

    class Config:
        env_file = ".env"
        case_sensitive = True
        env_file_encoding = 'utf-8'
        extra = "allow"

    @property
    def allowed_origins(self) -> List[str]:
        return [
            "http://localhost:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174",
            "http://localhost:8001",
            "http://127.0.0.1:8001"
        ]

admin_settings = AdminSettings() 