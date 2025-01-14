from fastapi import APIRouter, Depends, HTTPException, status as http_status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.db.session import get_db
from app.core.auth import get_current_admin
from app.models.betting_code import BettingCode
from app.models.user import User
from app.models.admin import Admin
from app.models.transaction import Transaction
from app.core.websocket_manager import manager
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/pending", response_model=List[dict])
async def get_pending_codes(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
    status: str = None
):
    """Get betting codes for admin's country with optional status filter"""
    try:
        country = current_admin.country.lower()
        logger.info(f"Admin {current_admin.id} fetching codes for {country}")
        
        query = db.query(
            BettingCode.id,
            BettingCode.bookmaker,
            BettingCode.code,
            BettingCode.odds,
            BettingCode.stake,
            BettingCode.potential_winnings,
            BettingCode.status,
            BettingCode.created_at,
            User.name.label('user_name'),
            User.email.label('user_email'),
            User.id.label('user_id'),
            User.country.label('user_country')
        ).join(User).filter(
            func.lower(User.country) == country
        )
        
        # Apply status filter if provided
        if status and status != 'all':
            query = query.filter(BettingCode.status == status)
            
        codes = query.order_by(BettingCode.created_at.desc()).all()
        
        logger.info(f"Found {len(codes)} codes")
        
        result = [{
            "id": code.id,
            "user_id": code.user_id,
            "user_name": code.user_name,
            "user_email": code.user_email,
            "user_country": code.user_country,
            "bookmaker": code.bookmaker,
            "code": code.code,
            "odds": code.odds,
            "stake": code.stake,
            "potential_winnings": code.potential_winnings,
            "status": code.status,
            "created_at": code.created_at
        } for code in codes]
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching pending codes: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch pending codes: {str(e)}"
        )

@router.post("/{code_id}/verify")
async def verify_code(
    code_id: int,
    status: str,
    note: str = None,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Verify a betting code"""
    try:
        # Get the betting code with user info
        code = db.query(BettingCode, User).join(User).filter(
            BettingCode.id == code_id
        ).first()
        
        if not code:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Betting code not found"
            )
            
        betting_code, user = code
        
        # Verify admin has access to this country
        if current_admin.country.lower() != user.country.lower():
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="Not authorized to verify codes for this country"
            )
            
        # Update code status
        betting_code.status = status
        betting_code.verified_by = current_admin.id
        betting_code.admin_note = note
        betting_code.verified_at = func.now()
        
        # Initialize notification data
        notification_data = {
            "code_id": betting_code.id,
            "status": status,
            "note": note,
            "reward_amount": 0,
            "new_balance": user.balance
        }
        
        # Calculate and add reward if code is won
        if status == 'won':
            # Calculate reward (odds * 2)
            reward_amount = betting_code.odds * 2
            
            logger.info(f"=== REWARD CALCULATION START ===")
            logger.info(f"Code ID: {betting_code.id}")
            logger.info(f"User ID: {user.id}")
            logger.info(f"Initial balance: {user.balance}")
            logger.info(f"Odds: {betting_code.odds}")
            logger.info(f"Reward calculation: {betting_code.odds} * 2 = {reward_amount}")
            
            # Update user balance
            old_balance = user.balance
            user.balance += reward_amount
            
            logger.info(f"=== BALANCE UPDATE ===")
            logger.info(f"Old balance: {old_balance}")
            logger.info(f"Reward amount: {reward_amount}")
            logger.info(f"New balance (before commit): {user.balance}")
            
            # Create transaction record with unique reference including timestamp
            timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            transaction = Transaction(
                user_id=user.id,
                amount=reward_amount,
                type='reward',
                status='completed',
                payment_method='system',
                payment_reference=f'WIN-{betting_code.id}-{timestamp}',
                description=f'Reward for winning bet {betting_code.code}',
                currency='NGN' if user.country.lower() == 'nigeria' else 'GHS'
            )
            db.add(transaction)
            
            logger.info(f"=== TRANSACTION CREATED ===")
            logger.info(f"Transaction type: reward")
            logger.info(f"Transaction amount: {reward_amount}")
            logger.info(f"Transaction status: completed")
            
            try:
                db.flush()  # Flush changes to get transaction ID
                logger.info(f"=== FLUSH SUCCESSFUL ===")
                logger.info(f"Transaction ID: {transaction.id}")
                
                # Update notification data with reward info
                notification_data["reward_amount"] = reward_amount
                notification_data["new_balance"] = user.balance
                notification_data["transaction_id"] = transaction.id
                
            except Exception as e:
                logger.error(f"=== FLUSH FAILED ===")
                logger.error(f"Error: {str(e)}")
                raise
        
        try:
            logger.info(f"=== COMMITTING CHANGES ===")
            db.commit()
            logger.info(f"=== COMMIT SUCCESSFUL ===")
            
            db.refresh(user)  # Refresh user to get updated balance
            logger.info(f"=== USER REFRESHED ===")
            logger.info(f"Final user balance after refresh: {user.balance}")
            
            # Update notification data with final balance
            notification_data["new_balance"] = user.balance
            
            if status == 'won':
                db.refresh(transaction)  # Refresh transaction to get ID
                logger.info(f"=== TRANSACTION REFRESHED ===")
                logger.info(f"Final transaction ID: {transaction.id}")
                
            logger.info(f"Successfully verified code {betting_code.id}")
            logger.info(f"Notification data: {notification_data}")
            
        except Exception as e:
            logger.error(f"=== COMMIT FAILED ===")
            logger.error(f"Error: {str(e)}")
            db.rollback()
            raise
        
        # Notify user through WebSocket
        await manager.notify_code_verification(user.email, notification_data)
        
        return {
            "message": "Code verified successfully",
            "reward_amount": notification_data["reward_amount"],
            "new_balance": notification_data["new_balance"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying code: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify code: {str(e)}"
        )

@router.post("/bulk-verify")
async def bulk_verify_codes(
    user_id: int,
    status: str,
    note: str = None,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Bulk verify all pending codes for a user"""
    try:
        # Get user info
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        # Verify admin has access to this country
        if current_admin.country.lower() != user.country.lower():
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="Not authorized to verify codes for this country"
            )
            
        # Get all pending codes for user
        codes = db.query(BettingCode).filter(
            BettingCode.user_id == user_id,
            BettingCode.status == 'pending'
        ).all()
        
        # Update all codes
        for code in codes:
            code.status = status
            code.verified_by = current_admin.id
            code.admin_note = note or f"Bulk verification: {status}"
            code.verified_at = func.now()
            
            # Notify user through WebSocket
            await manager.notify_code_verification(
                user.email,
                code.id,
                status,
                note or f"Bulk verification: {status}"
            )
        
        db.commit()
        
        return {
            "message": f"Successfully verified {len(codes)} codes",
            "verified_count": len(codes)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error bulk verifying codes: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk verify codes: {str(e)}"
        )