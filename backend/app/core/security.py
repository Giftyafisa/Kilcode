from fastapi import Request, HTTPException, Depends, status
from typing import Optional, List, Any, Union
from datetime import datetime, timedelta
import ipaddress
import logging
from passlib.context import CryptContext
from jose import jwt, JWTError
from .config import settings
from .admin_config import admin_settings
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ..core.admin_database import AdminSessionLocal
from ..models.admin import Admin
import os

# Set up logging
logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Add explicit rounds
)

# OAuth2 scheme for token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Get DB Session
def get_admin_db():
    db = AdminSessionLocal()
    try:
        yield db
    finally:
        db.close()

class SecurityManager:
    def __init__(self):
        # Development mode - skip GeoIP
        self.reader = None
        self.blocked_ips: List[str] = []
        self.country_restrictions = {
            'nigeria': {
                'allowed_countries': ['NG'],
                'max_requests_per_minute': 60,
                'max_failed_attempts': 5,
                'required_headers': ['X-Device-ID']
            },
            'ghana': {
                'allowed_countries': ['GH'],
                'max_requests_per_minute': 60,
                'max_failed_attempts': 5,
                'required_headers': ['X-Device-ID']
            }
        }

    def create_access_token(
        self,
        data: dict,
        expires_delta: Optional[timedelta] = None,
        secret_key: Optional[str] = None
    ) -> str:
        """Create JWT access token with payload data"""
        try:
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(
                    minutes=admin_settings.ADMIN_TOKEN_EXPIRE_MINUTES
                )
            
            # Add additional claims
            to_encode = data.copy()
            to_encode.update({
                "exp": expire,
                "iat": datetime.utcnow(),
            })
            
            # Use provided secret key or determine based on token type
            key_to_use = secret_key
            if not key_to_use:
                key_to_use = (
                    admin_settings.ADMIN_SECRET_KEY 
                    if data.get("type") == "admin" 
                    else settings.SECRET_KEY
                )
            
            encoded_jwt = jwt.encode(
                to_encode, 
                key_to_use, 
                algorithm=settings.ALGORITHM
            )
            return encoded_jwt
        except Exception as e:
            logger.error(f"Token creation error: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Could not create access token"
            )

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Password verification error: {str(e)}")
            return False

    def get_password_hash(self, password: str) -> str:
        """Generate password hash"""
        try:
            return pwd_context.hash(password)
        except Exception as e:
            logger.error(f"Password hashing error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Could not process password"
            )

    async def verify_request(self, request: Request, country: str) -> bool:
        # Development mode - skip most checks
        client_ip = request.client.host
        
        # Only check if IP is blocked
        if client_ip in self.blocked_ips:
            raise HTTPException(status_code=403, detail="IP address blocked")

        return True

    async def verify_country(self, ip: str, service_country: str) -> bool:
        # Development mode - always return True
        return True

    def verify_headers(self, request: Request, country: str) -> bool:
        # Development mode - skip header checks
        return True

# Create a single instance
security_manager = SecurityManager()

# For backwards compatibility with existing code
create_access_token = security_manager.create_access_token
verify_password = security_manager.verify_password
get_password_hash = security_manager.get_password_hash

async def get_current_admin(
    db: Session = Depends(get_admin_db),
    token: str = Depends(oauth2_scheme)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Use admin secret key instead of regular secret key
        payload = jwt.decode(
            token, 
            admin_settings.ADMIN_SECRET_KEY,  # Changed this line
            algorithms=[settings.ALGORITHM]
        )
        admin_id: str = payload.get("sub")
        if admin_id is None:
            logger.error("No admin_id found in token")
            raise credentials_exception
            
        # Add role check
        if payload.get("role") not in ["super_admin", "country_admin"]:
            logger.error(f"Invalid admin role: {payload.get('role')}")
            raise credentials_exception
            
        admin = db.query(Admin).filter(
            Admin.id == int(admin_id),
            Admin.is_active == True
        ).first()
        
        if not admin:
            logger.error(f"No active admin found with id: {admin_id}")
            raise credentials_exception
            
        # Verify admin's role matches token
        if admin.role != payload.get("role"):
            logger.error(f"Role mismatch: token={payload.get('role')}, db={admin.role}")
            raise credentials_exception
            
        return admin
        
    except JWTError as e:
        logger.error(f"JWT validation error: {str(e)}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error in admin authentication: {str(e)}")
        raise credentials_exception