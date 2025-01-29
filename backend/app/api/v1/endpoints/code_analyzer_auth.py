from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.admin_session import get_admin_db
from app.core.auth import get_current_admin
from app.models.admin import Admin
from app.core import security
from pydantic import BaseModel, EmailStr
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/login")
async def login(
    request: LoginRequest,
    db: Session = Depends(get_admin_db)
):
    """Login for code analyzer admins with robust error handling"""
    try:
        logger.info(f"Code analyzer login attempt for email: {request.email}")
        
        # Validate input
        if not request.email or not request.password:
            logger.warning("Login attempt with missing credentials")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password are required"
            )
        
        # Get admin user
        admin = db.query(Admin).filter(Admin.email == request.email).first()
        if not admin:
            logger.warning(f"Admin not found: {request.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
            
        # Verify password
        if not security.verify_password(request.password, admin.hashed_password):
            logger.warning(f"Invalid password for admin: {request.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
            
        # Create access token
        access_token = security.create_access_token(
            data={
                "sub": str(admin.id),
                "email": admin.email,
                "type": "code_analyzer",
                "role": admin.role
            }
        )
        
        logger.info(f"Successful login for admin: {request.email}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "email": admin.email,
            "role": admin.role
        }
    except HTTPException as http_exc:
        # Re-raise HTTPExceptions as they are intentional
        logger.warning(f"Authentication error: {http_exc.detail}")
        raise
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error during login: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during authentication"
        )

@router.get("/verify")
async def verify_token(
    current_admin: Admin = Depends(get_current_admin)
):
    """Verify token and return admin info"""
    return {
        "id": current_admin.id,
        "email": current_admin.email,
        "role": current_admin.role,
        "country": current_admin.country
    } 