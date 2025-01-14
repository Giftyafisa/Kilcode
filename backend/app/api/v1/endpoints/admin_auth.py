from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Any
import logging
from datetime import timedelta

from app.schemas.token import TokenResponse
from app.schemas.admin import AdminLogin, AdminCreate, Admin, AdminResponse
from app.db.admin_session import get_admin_db
from app.core.security import security_manager
from app.core.config import settings
from app.core.auth import get_current_admin
from app import crud

router = APIRouter()
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.get("/verify", response_model=AdminResponse)
async def verify_token(
    current_admin: Admin = Depends(get_current_admin),
) -> Any:
    """
    Verify admin token and return admin info
    """
    try:
        logger.info(f"Token verification for admin: {current_admin.email}")
        return AdminResponse(
            token="",  # Token is sent in header, no need to return
            email=current_admin.email,
            role=current_admin.role,
            country=current_admin.country,
            full_name=current_admin.full_name,
            id=current_admin.id  # Include admin ID
        )
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@router.post("/register", response_model=Admin)
async def register_admin(
    *,
    db: Session = Depends(get_admin_db),
    admin_in: AdminCreate,
) -> Any:
    """
    Register a new admin.
    """
    try:
        logger.info(f"Admin registration attempt for email: {admin_in.email}")
        
        # Check if admin already exists
        admin = crud.admin.get_by_email(db, email=admin_in.email)
        if admin:
            logger.warning(f"Admin registration failed - email already exists: {admin_in.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new admin
        admin = crud.admin.create(db, obj_in=admin_in)
        logger.info(f"Admin registered successfully: {admin_in.email}")
        
        return admin
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error during admin registration: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred"
        )

@router.post("/login", response_model=AdminResponse)
async def admin_login(
    *,
    db: Session = Depends(get_admin_db),
    form_data: AdminLogin,
) -> Any:
    """
    Admin login endpoint
    """
    try:
        logger.info(f"Admin login attempt for email: {form_data.email}")
        
        admin = crud.admin.authenticate(
            db, 
            email=form_data.email, 
            password=form_data.password
        )
        
        if not admin:
            logger.warning(f"Failed admin login attempt for email: {form_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
            
        if not admin.is_active:
            logger.warning(f"Inactive admin attempt to login: {form_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive admin account"
            )
        
        # Create token payload with correct type
        token_data = {
            "sub": str(admin.id),
            "email": admin.email,
            "type": "admin",
            "role": admin.role,
            "country": admin.country
        }
        
        # Create access token
        expires_delta = timedelta(minutes=settings.ADMIN_TOKEN_EXPIRE_MINUTES)
        access_token = security_manager.create_access_token(
            data=token_data,
            expires_delta=expires_delta,
            secret_key=settings.ADMIN_SECRET_KEY
        )
        
        logger.info(f"Creating token with payload: {token_data}")
        
        return AdminResponse(
            token=access_token,
            email=admin.email,
            role=admin.role,
            country=admin.country,
            full_name=admin.full_name,
            id=admin.id  # Include admin ID
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error during admin login: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred"
        ) 