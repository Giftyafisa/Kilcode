from typing import Any, Dict, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas import UserCreate, UserUpdate

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email.ilike(email)).first()
    
    def get_by_phone(self, db: Session, *, phone: str) -> Optional[User]:
        user = db.query(User).filter(User.phone == phone).first()
        return user

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        # Normalize email and country
        email = obj_in.email.lower().strip()
        country = obj_in.country.lower().strip()
        
        if country not in ('nigeria', 'ghana'):
            raise ValueError("Country must be either 'nigeria' or 'ghana'")
            
        db_obj = User(
            email=email,
            hashed_password=get_password_hash(obj_in.password),
            name=obj_in.name,
            country=country,
            phone=obj_in.phone,
            is_active=True,
            is_verified=False,
            payment_status='pending',
            balance=0.0
        )
        db.add(db_obj)
        try:
            db.commit()
            db.refresh(db_obj)
            # Add default status if column doesn't exist
            if not hasattr(db_obj, 'status'):
                setattr(db_obj, 'status', 'active')
            return db_obj
        except Exception as e:
            db.rollback()
            raise e

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_verified(self, user: User) -> bool:
        return user.is_verified

    def update_balance(self, db: Session, *, user_id: int, amount: float) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
            
        user.balance += amount
        db.commit()
        db.refresh(user)
        return user

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> list[User]:
        """Get multiple users with pagination"""
        # Build query with only existing columns
        query = db.query(
            User.id,
            User.email,
            User.name,
            User.country,
            User.phone,
            User.balance,
            User.created_at,
            User.updated_at,
            User.is_active,
            User.is_verified,
            User.payment_status,
            User.payment_reference,
        )
        
        users = query.offset(skip).limit(limit).all()
        
        # Add default status if column doesn't exist
        for user in users:
            if not hasattr(user, 'status'):
                setattr(user, 'status', 'active')
                
        return users

    def update(self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
            
        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])
                
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

user = CRUDUser(User) 