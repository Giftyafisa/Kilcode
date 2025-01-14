from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import List, Dict, Any
from datetime import datetime, timedelta

from ....db.admin_session import get_admin_db
from ....core.auth import get_current_admin
from ....models.user import User
from ....models.transaction import Transaction
from ....models.betting_code import BettingCode
from ....models.activity import Activity

router = APIRouter()

@router.get("/overview")
async def get_statistics_overview(
    db: Session = Depends(get_admin_db),
    current_admin: User = Depends(get_current_admin)
) -> Dict[str, Any]:
    """Get overview statistics for the admin dashboard"""
    
    # Get total users
    total_users = db.query(func.count(User.id)).scalar()
    
    # Get total transactions
    total_transactions = db.query(func.count(Transaction.id)).scalar()
    
    # Get total betting codes
    total_betting_codes = db.query(func.count(BettingCode.id)).scalar()
    
    # Get total activities
    total_activities = db.query(func.count(Activity.id)).scalar()
    
    # Get recent transactions
    recent_transactions = (
        db.query(Transaction)
        .order_by(Transaction.created_at.desc())
        .limit(5)
        .all()
    )
    
    # Get recent betting codes
    recent_betting_codes = (
        db.query(BettingCode)
        .order_by(BettingCode.created_at.desc())
        .limit(5)
        .all()
    )
    
    return {
        "total_users": total_users,
        "total_transactions": total_transactions,
        "total_betting_codes": total_betting_codes,
        "total_activities": total_activities,
        "recent_transactions": [
            {
                "id": t.id,
                "amount": t.amount,
                "type": t.type,
                "status": t.status,
                "created_at": t.created_at
            }
            for t in recent_transactions
        ],
        "recent_betting_codes": [
            {
                "id": b.id,
                "code": b.code,
                "odds": b.odds,
                "status": b.status,
                "created_at": b.created_at
            }
            for b in recent_betting_codes
        ]
    } 