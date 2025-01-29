from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from typing import List, Literal, Optional, Dict, Any
import re
import logging
from app.core.auth import get_current_user
from app.schemas.user import User
from app.core.security import create_access_token
from app.api.v1.endpoints import (
    auth, payments, betting_codes, admin_dashboard, admin_auth,
    admin_statistics, admin_betting, admin_users,
    admin_verifications, admin_payments, code_analyzer, marketplace
)
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionListResponse, Transaction as TransactionSchema

# Set up logging
logger = logging.getLogger(__name__)

api_router = APIRouter()

# Include the auth router
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Include the payments router
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])

# Include the betting codes router
api_router.include_router(betting_codes.router, prefix="/betting-codes", tags=["betting-codes"])

# Include the admin dashboard router
api_router.include_router(admin_dashboard.router, prefix="/admin/dashboard", tags=["admin"])

# Include the admin auth router
api_router.include_router(admin_auth.router, prefix="/admin/auth", tags=["admin"])

# Include the admin statistics router
api_router.include_router(admin_statistics.router, prefix="/admin/statistics", tags=["admin"])

# Include the admin betting router
api_router.include_router(admin_betting.router, prefix="/admin/betting-codes", tags=["admin"])

# Include the admin users router
api_router.include_router(admin_users.router, prefix="/admin/users", tags=["admin"])

# Include the admin verifications router
api_router.include_router(
    admin_verifications.router,
    prefix="/admin/verifications",
    tags=["admin"]
)
6
# Include the admin payments router
api_router.include_router(
    admin_payments.router,
    prefix="/admin/payments",
    tags=["admin"]
)

# Include the marketplace router
api_router.include_router(
    marketplace.router,
    prefix="/marketplace",
    tags=["marketplace"]
)

# Include the code analyzer router
api_router.include_router(
    code_analyzer.router,
    prefix="/code-analyzer",
    tags=["code-analyzer"]
)

# Create models for our requests
class UserRegister(BaseModel):
    name: str
    email: str
    password: str
    country: str
    phone: str

class UserLogin(BaseModel):
    email: str
    password: str

class BettingCodeCreate(BaseModel):
    bookmaker: str
    code: str
    odds: float
    game_count: int
    country: str

class BettingCodeResponse(BaseModel):
    id: int
    bookmaker: str
    code: str
    odds: float
    status: str
    created_at: datetime

class TransactionCreate(BaseModel):
    type: Literal['withdrawal', 'deposit']
    amount: float = Field(..., gt=0)
    payment_method: str
    currency: Literal['NGN', 'GHS']

class TransactionResponse(BaseModel):
    id: int
    type: str
    amount: float
    status: str
    reference: str
    payment_method: str
    currency: str
    created_at: datetime

class NotificationBase(BaseModel):
    id: int
    title: str
    message: str
    type: str
    read: bool
    created_at: datetime

class SyncRequest(BaseModel):
    lastSync: str
    version: str

class SyncResponse(BaseModel):
    updates: List[Dict[str, Any]]
    newVersion: str

# For development, you can make the auth optional
async def get_optional_user(request: Request) -> Optional[User]:
    try:
        # Try to get authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None
            
        token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else None
        if not token:
            return None
            
        user = await get_current_user(token)
        return user
    except:
        return None

@api_router.get("/test")
async def test():
    return {"message": "API router is working"}

@api_router.get("/betting-codes/user/codes", response_model=List[BettingCodeResponse])
async def get_user_codes():
    # For testing, return mock data
    return [
        {
            "id": 1,
            "bookmaker": "Bet9ja",
            "code": "B9J-123456-ABCD",
            "odds": 2.5,
            "status": "pending",
            "created_at": datetime.now()
        }
    ]

@api_router.post("/betting-codes/submit", response_model=BettingCodeResponse)
async def submit_betting_code(code: BettingCodeCreate):
    # Validate code format based on bookmaker and country
    if not validate_betting_code(code.code, code.bookmaker, code.country):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid code format for {code.bookmaker}"
        )

    # For testing, return mock data
    return {
        "id": 2,
        "bookmaker": code.bookmaker,
        "code": code.code,
        "odds": code.odds,
        "status": "pending",
        "created_at": datetime.now(),
        "game_count": code.game_count,
        "country": code.country
    }

def validate_betting_code(code: str, bookmaker: str, country: str) -> bool:
    patterns = {
        'bet9ja': r'^(B9J-)?[A-Z0-9]{6}-[A-Z0-9]{4}$',
        'sportybet': r'^(SB-)?[A-Z0-9]{8}$',
        '1xbet': r'^(1X-)?[A-Z0-9]{8,12}$',
        'betway': r'^(BW-)?[A-Z0-9]{8}$',
        'betpawa': r'^(BP-)?[A-Z0-9]{8}$'
    }
    
    if bookmaker not in patterns:
        return False
        
    return bool(re.match(patterns[bookmaker], code, re.IGNORECASE)) 

@api_router.get("/transactions", response_model=TransactionListResponse)
async def get_transactions(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user transactions and current balance"""
    try:
        # Get user with fresh balance
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get all transactions for user
        transactions = db.query(Transaction)\
            .filter(Transaction.user_id == user.id)\
            .order_by(Transaction.created_at.desc())\
            .all()

        # Calculate balance from transactions
        total_rewards = sum(
            t.amount for t in transactions 
            if t.type == 'reward' and t.status == 'completed'
        )
        total_withdrawals = sum(
            (t.amount + (t.fee or 0)) for t in transactions 
            if t.type == 'withdrawal' and t.status == 'completed'
        )
        calculated_balance = total_rewards - total_withdrawals

        # If calculated balance differs from stored balance, update it
        if abs(user.balance - calculated_balance) > 0.01:
            user.balance = calculated_balance
            db.commit()
            db.refresh(user)

        # Convert transactions to Pydantic models
        transaction_schemas = [TransactionSchema.model_validate(t) for t in transactions]

        return TransactionListResponse(
            balance=user.balance,
            transactions=transaction_schemas
        )

    except Exception as e:
        logger.error(f"Error getting transactions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get transactions"
        )

@api_router.post("/transactions", response_model=TransactionResponse)
async def create_transaction(transaction: TransactionCreate):
    # Validate transaction based on country and payment method
    if transaction.currency == "NGN" and transaction.amount < 100:
        raise HTTPException(
            status_code=400,
            detail="Minimum transaction amount is ₦100"
        )
    elif transaction.currency == "GHS" and transaction.amount < 1:
        raise HTTPException(
            status_code=400,
            detail="Minimum transaction amount is GH₵1"
        )

    # For testing, return mock data
    return {
        "id": 3,
        "type": transaction.type,
        "amount": transaction.amount,
        "status": "pending",
        "reference": f"TRX-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "payment_method": transaction.payment_method,
        "currency": transaction.currency,
        "created_at": datetime.now()
    }

@api_router.get("/health")
async def health_check(current_user: User = Depends(get_optional_user)):
    """
    Health check endpoint for WebSocket fallback
    """
    return {
        "status": "healthy",
        "user_id": current_user.id if current_user else None,
        "timestamp": datetime.now().isoformat()
    }

@api_router.get("/updates")
async def get_updates(current_user: User = Depends(get_optional_user)) -> Dict[str, List[Any]]:
    """
    Polling endpoint for when WebSocket is unavailable
    """
    # Mock updates for testing
    updates = []
    if current_user:
        updates = [
            {
                "type": "SYSTEM_MESSAGE",
                "message": "Connected to polling updates"
            }
            # Add any pending notifications or updates from your database here
        ]
    
    return {"updates": updates} 

@api_router.post("/sync", response_model=SyncResponse)
async def sync_data(
    sync_request: SyncRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        # Convert lastSync from timestamp string to datetime
        last_sync_dt = datetime.fromtimestamp(int(sync_request.lastSync) / 1000)
        
        updates = []
        
        # Add mock updates for testing
        updates.extend([
            {
                "type": "CODE_STATUS",
                "code": "B9J-123456-ABCD",
                "status": "verified",
                "updated_at": datetime.now().timestamp() * 1000,
                "message": "Code verified successfully"
            },
            {
                "type": "PAYMENT_STATUS",
                "reference": "TRX-123456",
                "status": "completed",
                "updated_at": datetime.now().timestamp() * 1000,
                "amount": 5000
            },
            {
                "type": "USER_SETTINGS",
                "settings": {
                    "notifications_enabled": True,
                    "language": "en",
                    "timezone": "Africa/Lagos"
                },
                "updated_at": datetime.now().timestamp() * 1000
            }
        ])

        # Generate new version (increment current version)
        new_version = str(int(sync_request.version) + 1)

        return SyncResponse(
            updates=updates,
            newVersion=new_version
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sync data: {str(e)}"
        ) 