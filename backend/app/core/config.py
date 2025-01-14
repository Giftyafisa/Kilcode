from pydantic_settings import BaseSettings
from typing import Optional, List
import secrets

class Settings(BaseSettings):
    # Project info
    PROJECT_NAME: str = "BoltSB"
    VERSION: str = "1.0.0"
    
    # Database settings
    DATABASE_URL: str
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = None
    DB_NAME: Optional[str] = None

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # Environment
    ENVIRONMENT: str = "development"

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000"

    # API
    API_V1_STR: str = "/api/v1"

    # WebSocket settings
    WS_URL: str = "ws://localhost:8000"

    # Payment settings
    PAYSTACK_SECRET_KEY: str
    PAYSTACK_PUBLIC_KEY: str
    PAYSTACK_WEBHOOK_SECRET: Optional[str] = None
    PAYSTACK_BASE_URL: str = "https://api.paystack.co"

    # Country-specific payment settings
    GHANA_REGISTRATION_FEE: float = 200.00  # GHS
    NIGERIA_REGISTRATION_FEE: float = 21927.00  # NGN
    
    # Admin settings
    ADMIN_API_PORT: int = 8001
    ADMIN_SECRET_KEY: str
    ADMIN_DATABASE_URL: str
    ADMIN_TOKEN_EXPIRE_MINUTES: int = 1440

    # Main backend settings
    MAIN_BACKEND_URL: str = "http://localhost:8000"

    @property
    def CORS_ORIGINS(self) -> List[str]:
        if not self.ALLOWED_ORIGINS:
            return []
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"

settings = Settings() 