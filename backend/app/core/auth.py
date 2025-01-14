from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session
from typing import Generator, Optional
import logging

from app import crud, models, schemas
from app.core.config import settings
from app.db.session import get_db
from app.db.admin_session import get_admin_db, AdminSessionLocal
from app.models.admin import Admin

logger = logging.getLogger(__name__)

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> models.User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
        
        # Convert string ID to integer
        try:
            user_id = int(token_data.sub) if token_data.sub else None
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid user ID format",
            )
            
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No user ID in token",
            )
            
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
        
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_admin(
    db: Session = Depends(get_admin_db),
    token: str = Depends(reusable_oauth2)
) -> Admin:
    """Get current admin for regular routes"""
    try:
        payload = jwt.decode(
            token, settings.ADMIN_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
        
        # Verify this is an admin token
        if not payload.get("type") == "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not an admin token",
            )
            
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate admin credentials",
        )
    admin = crud.admin.get(db, id=token_data.sub)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    if not admin.is_active:
        raise HTTPException(status_code=400, detail="Inactive admin")
    return admin

async def get_current_user_ws(token: str) -> Optional[models.User]:
    """Authenticate user via WebSocket token"""
    try:
        if not token:
            logger.warning("No token provided")
            return None
            
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
        
        # Convert string ID to integer
        try:
            user_id = int(token_data.sub) if token_data.sub else None
        except (TypeError, ValueError):
            logger.error(f"Invalid user ID format: {token_data.sub}")
            return None
            
        if not user_id:
            logger.warning("No user ID in token")
            return None
            
        db = next(get_db())
        try:
            user = crud.user.get(db, id=user_id)
            if not user:
                logger.warning(f"User not found for id {user_id}")
                return None
                
            if not user.is_active:
                logger.warning(f"User {user.email} is not active")
                return None
                
            if not user.country:
                logger.warning(f"No country set for user {user.email}")
                return None
                
            if user.country.lower() not in ['ghana', 'nigeria']:
                logger.warning(f"Invalid country {user.country} for user {user.email}")
                return None
                
            return user
            
        finally:
            db.close()
            
    except (JWTError, ValidationError) as e:
        logger.error(f"Token validation error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user_ws: {str(e)}")
        return None

async def get_current_admin_ws(token: str) -> Optional[Admin]:
    """Authenticate admin via WebSocket token"""
    try:
        if not token:
            return None
            
        payload = jwt.decode(
            token, settings.ADMIN_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        
        # Verify this is an admin token
        if payload.get("type") != "admin" or payload.get("role") != "country_admin":
            logger.warning("Token is not a valid admin token")
            return None
            
        token_data = schemas.TokenPayload(**payload)
        
        # Use admin database session
        db = AdminSessionLocal()
        try:
            admin = crud.admin.get(db, id=token_data.sub)
            if not admin or not admin.is_active:
                logger.warning("Admin not found or inactive")
                return None
            return admin
        finally:
            db.close()
            
    except (JWTError, ValidationError) as e:
        logger.error(f"Token validation error: {str(e)}")
        return None