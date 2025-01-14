from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, WebSocket
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal
from app.db.admin_session import AdminSessionLocal
from app.models.admin import Admin
import logging

logger = logging.getLogger(__name__)

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> models.User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
        user_id = token_data.sub
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
    except (JWTError, ValidationError) as e:
        logger.error(f"Token validation error: {str(e)}")
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

def get_current_admin(
    db: Session = Depends(get_db),
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