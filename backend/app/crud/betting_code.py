from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.crud.base import CRUDBase
from app.models.betting_code import BettingCode
from app.models.user import User
from app.schemas.betting_code import BettingCodeCreate, BettingCodeUpdate

class CRUDBettingCode(CRUDBase[BettingCode, BettingCodeCreate, BettingCodeUpdate]):
    def create_with_user(
        self, 
        db: Session, 
        *, 
        obj_in: BettingCodeCreate, 
        user_id: int
    ) -> BettingCode:
        """Create a new betting code for a user"""
        # Get user for validation
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
            
        # Validate user country
        if not obj_in.user_country:
            raise ValueError("User country is required")
            
        # Ensure user_country matches user's country
        if obj_in.user_country.lower() != user.country.lower():
            raise ValueError(f"User country mismatch. Expected {user.country}, got {obj_in.user_country}")
        
        # Calculate potential winnings
        potential_winnings = obj_in.odds * obj_in.stake
        
        # Create database object with only the required fields for initial submission
        db_obj = BettingCode(
            user_id=user_id,
            bookmaker=obj_in.bookmaker,
            code=obj_in.code,
            odds=obj_in.odds,
            stake=obj_in.stake,
            potential_winnings=potential_winnings,
            status='pending'  # Always start as pending
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj

    def get_by_user(
        self, 
        db: Session, 
        *, 
        user_id: int,
        skip: int = 0,
        limit: int = 10,
        status: Optional[str] = None,
        sort: str = "created_at",
        direction: str = "desc"
    ) -> List[BettingCode]:
        """Get betting codes for a specific user with pagination and filtering"""
        query = db.query(BettingCode).filter(BettingCode.user_id == user_id)
        
        # Apply status filter if provided
        if status:
            query = query.filter(BettingCode.status == status)
            
        # Apply sorting
        sort_column = getattr(BettingCode, sort, BettingCode.created_at)
        if direction == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
            
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        return query.all()
    
    def get_pending_by_country(self, db: Session, *, country: str) -> List[BettingCode]:
        return (
            db.query(BettingCode)
            .join(User)
            .filter(
                BettingCode.status == "pending",
                func.lower(User.country) == country.lower()
            )
            .all()
        )

    def verify_code(
        self,
        db: Session,
        *,
        betting_code_id: int,
        admin_id: int,
        status: str,
        admin_note: Optional[str] = None,
        rejection_reason: Optional[str] = None
    ) -> BettingCode:
        db_obj = db.query(BettingCode).filter(BettingCode.id == betting_code_id).first()
        if not db_obj:
            return None
        
        db_obj.status = status
        db_obj.verified_by = admin_id
        db_obj.verified_at = datetime.utcnow()
        db_obj.admin_note = admin_note
        db_obj.rejection_reason = rejection_reason
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def check_daily_limit(self, db: Session, *, user_id: int) -> bool:
        today = datetime.utcnow().date()
        daily_count = (
            db.query(func.count(BettingCode.id))
            .filter(
                BettingCode.user_id == user_id,
                func.date(BettingCode.created_at) == today
            )
            .scalar()
        )
        return daily_count >= 10  # Maximum 10 codes per day

betting_code = CRUDBettingCode(BettingCode) 