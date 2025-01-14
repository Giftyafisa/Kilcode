from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy import func, inspect
from sqlalchemy.orm import Session
from app.core.security import get_current_admin
from app.schemas.user import User, UserUpdate, UserStatusUpdate
from app.models.user import User as UserModel
from app.crud.user import user as user_crud
from app.db.session import get_db
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/users", response_model=List[User])
async def get_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_admin = Depends(get_current_admin)
):
    """Get users from admin's country with pagination"""
    try:
        logger.info(f"Fetching users for admin country: {current_admin.country}")
        
        # Get list of existing columns
        inspector = inspect(db.get_bind())
        columns = [c['name'] for c in inspector.get_columns('users')]
        
        # Build query
        query = db.query(UserModel)
        
        # Filter by admin's country
        query = query.filter(func.lower(UserModel.country) == func.lower(current_admin.country))
        
        # Add ordering
        query = query.order_by(UserModel.created_at.desc())
        
        # Add pagination
        users = query.offset(skip).limit(limit).all()
        
        # Convert to response format
        response = []
        for user in users:
            user_dict = {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'country': user.country,
                'phone': user.phone,
                'balance': user.balance,
                'created_at': user.created_at,
                'updated_at': user.updated_at,
                'is_active': user.is_active,
                'is_verified': user.is_verified,
                'payment_status': user.payment_status if hasattr(user, 'payment_status') else None,
                'payment_reference': user.payment_reference if hasattr(user, 'payment_reference') else None,
                'status': user.status if hasattr(user, 'status') else 'active'
            }
            response.append(user_dict)
        
        logger.info(f"Found {len(response)} users")
        return response
        
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error while fetching users: {str(e)}"
        )

@router.post("/users/{user_id}/status", response_model=User)
async def update_user_status(
    user_id: int,
    status_update: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Update user status"""
    try:
        # Check if status column exists
        inspector = inspect(db.get_bind())
        has_status = 'status' in [c['name'] for c in inspector.get_columns('users')]
        
        if not has_status:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status updates are not supported yet. Please run migrations first."
            )
        
        # Get user and check if they belong to admin's country
        user = db.query(UserModel).filter(
            UserModel.id == user_id,
            func.lower(UserModel.country) == func.lower(current_admin.country)
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="User not found or not in your country"
            )
        
        # Validate status value
        valid_statuses = ["active", "suspended", "pending"]
        if status_update.status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        user_update = UserUpdate(status=status_update.status)
        updated_user = user_crud.update(db, db_obj=user, obj_in=user_update)
        
        logger.info(f"Updated user {user_id} status to {status_update.status}")
        return updated_user
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating user status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while updating user status"
        ) 