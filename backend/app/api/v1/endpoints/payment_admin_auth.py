from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any
import logging
from datetime import timedelta

from app.schemas.token import TokenResponse
from app.schemas.admin import AdminLogin, Admin, AdminResponse
from app.db.admin_session import get_admin_db
from app.core.security import security_manager
from app.core.config import settings
from app.core.auth import get_current_admin
from app import crud

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/me", response_model=AdminResponse)
async def get_payment_admin_info(
    current_admin: Admin = Depends(get_current_admin),
) -> Any:
    """
    Get current payment admin info
    """
    try:
        logger.info(f"Getting payment admin info for: {current_admin.email} (Country: {current_admin.country})")
        return AdminResponse(
            token="",  # Token is sent in header
            email=current_admin.email,
            role=current_admin.role,
            country=current_admin.country,
            full_name=current_admin.full_name,
            id=current_admin.id
        )
    except Exception as e:
        logger.error(f"Error getting payment admin info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@router.post("/login", response_model=AdminResponse)
async def payment_admin_login(
    *,
    db: Session = Depends(get_admin_db),
    form_data: AdminLogin,
) -> Any:
    """
    Payment admin login endpoint with country-specific validation
    """
    try:
        logger.info(f"Payment admin login attempt for email: {form_data.email}")
        
        admin = crud.admin.authenticate(
            db, 
            email=form_data.email, 
            password=form_data.password
        )
        
        if not admin:
            logger.warning(f"Failed payment admin login attempt for email: {form_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
            
        if not admin.is_active:
            logger.warning(f"Inactive payment admin attempt to login: {form_data.email} (Country: {admin.country})")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive admin account"
            )

        # Validate admin has proper role and country assignment
        if not admin.country:
            logger.error(f"Admin {admin.email} has no country assigned")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admin account not properly configured - missing country"
            )
        
        # Create token payload with correct type and country
        token_data = {
            "sub": str(admin.id),
            "email": admin.email,
            "type": "payment_admin",  # Different type for payment admin
            "role": admin.role,
            "country": admin.country
        }
        
        # Create access token with different expiry
        expires_delta = timedelta(minutes=settings.ADMIN_TOKEN_EXPIRE_MINUTES)
        access_token = security_manager.create_access_token(
            data=token_data,
            expires_delta=expires_delta,
            secret_key=settings.ADMIN_SECRET_KEY
        )
        
        logger.info(f"Successful payment admin login for {admin.email} (Country: {admin.country}, Role: {admin.role})")
        
        return AdminResponse(
            token=access_token,
            email=admin.email,
            role=admin.role,
            country=admin.country,
            full_name=admin.full_name,
            id=admin.id
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error during payment admin login: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred"
        ) 