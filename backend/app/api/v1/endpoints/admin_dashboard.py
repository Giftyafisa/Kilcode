from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_
from typing import List
from ....db.session import get_db
from ....core.security import get_current_admin
from ....models.betting_code import BettingCode
from ....models.user import User
from ....models.admin import Admin
from ....models.payment import Payment
from ....models.transaction import Transaction
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/statistics")
async def get_statistics(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get country-specific statistics"""
    try:
        country = current_admin.country.lower()
        logger.info(f"Getting statistics for country: {country}")
        
        # User statistics - only for this admin's country
        total_users = db.query(User).filter(
            func.lower(User.country) == country
        ).count() or 0
        logger.info(f"Total users: {total_users}")
        
        # Active users
        active_users = db.query(User).filter(
            func.lower(User.country) == country,
            User.is_active == True
        ).count() or 0
        
        # Verified users
        verified_users = db.query(User).filter(
            func.lower(User.country) == country,
            User.is_verified == True
        ).count() or 0
        
        # Betting code statistics
        betting_stats = db.query(
            func.count(BettingCode.id).label('total_codes'),
            func.sum(case((BettingCode.status == 'pending', 1), else_=0)).label('pending_codes'),
            func.sum(case((BettingCode.status == 'won', 1), else_=0)).label('won_codes'),
            func.sum(case((BettingCode.status == 'lost', 1), else_=0)).label('lost_codes')
        ).join(User, isouter=True).filter(
            func.lower(User.country) == country
        ).first()
        logger.info(f"Betting stats: {betting_stats}")

        response = {
            "country": country.upper(),
            "users": {
                "total": total_users,
                "active": active_users,
                "verified": verified_users
            },
            "betting": {
                "total_codes": betting_stats.total_codes if betting_stats else 0,
                "pending_codes": betting_stats.pending_codes if betting_stats else 0,
                "won_codes": betting_stats.won_codes if betting_stats else 0,
                "lost_codes": betting_stats.lost_codes if betting_stats else 0
            }
        }
        logger.info(f"Returning statistics: {response}")
        return response
        
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/pending-verifications")
async def get_pending_verifications(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get pending betting code verifications for admin's country"""
    try:
        country = current_admin.country.lower()
        logger.info(f"Getting pending verifications for country: {country}")
        
        pending_codes = db.query(BettingCode).join(User).filter(
            func.lower(User.country) == country,
            BettingCode.status == 'pending'
        ).all()
        
        if not pending_codes:
            logger.info("No pending codes found")
            return []
            
        logger.info(f"Found {len(pending_codes)} pending codes")
        
        result = [{
            "id": code.id,
            "user_name": code.user.name if code.user else "Unknown",
            "bookmaker": code.bookmaker,
            "code": code.code,
            "odds": code.odds,
            "stake": code.stake,
            "potential_winnings": code.potential_winnings,
            "created_at": code.created_at
        } for code in pending_codes]
        
        logger.info(f"Returning pending verifications: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error getting pending verifications: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/pending-payments")
async def get_pending_payments(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get pending registration payments for admin's country"""
    try:
        country = current_admin.country.lower()
        logger.info(f"Getting pending payments for country: {country}")
        
        pending_payments = db.query(Payment).join(User).filter(
            func.lower(User.country) == country,
            Payment.status == 'pending'
        ).all()
        
        logger.info(f"Found {len(pending_payments)} pending payments")
        
        result = [{
            "id": payment.id,
            "user_name": payment.user.name,
            "user_email": payment.user.email,
            "amount": payment.amount,
            "payment_method": payment.payment_method,
            "reference": payment.reference,
            "created_at": payment.created_at
        } for payment in pending_payments]
        
        logger.info(f"Returning pending payments: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error getting pending payments: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/verify-code/{code_id}")
async def verify_code(
    code_id: int,
    status: str,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Verify betting code"""
    try:
        # Get code and check country
        code = db.query(BettingCode).join(User).filter(
            BettingCode.id == code_id
        ).first()
        
        if not code:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Betting code not found"
            )
            
        # Verify admin has access to this country
        if current_admin.country.lower() != code.user.country.lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized for this country"
            )
            
        # Update code status
        code.status = status
        code.verified_by = current_admin.id
        code.verified_at = func.now()
        
        # Create activity log
        activity = Activity(
            user_id=code.user_id,
            activity_type="betting_code_verification",
            description=f"Betting code {code.code} verified as {status}",
            activity_metadata={
                "code_id": code.id,
                "status": status,
                "verified_by": current_admin.id
            },
            country=code.user.country,
            status="success"
        )
        
        db.add(activity)
        db.commit()
        
        return {"message": f"Betting code verified as {status}"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying betting code: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify betting code"
        )

@router.post("/verify-payment/{payment_id}")
async def verify_payment(
    payment_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Verify user registration payment"""
    try:
        # Get payment and check country
        payment = db.query(Payment).join(User).filter(
            Payment.id == payment_id
        ).first()
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
            
        # Verify admin has access to this country
        if current_admin.country.lower() != payment.user.country.lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized for this country"
            )
            
        # Update payment status and user verification
        payment.status = 'completed'
        payment.verified_by = current_admin.id
        payment.verified_at = func.now()
        
        # Update user status
        payment.user.is_verified = True
        
        # Create activity log
        activity = Activity(
            user_id=payment.user_id,
            activity_type="payment_verification",
            description=f"Payment {payment.reference} verified",
            activity_metadata={
                "payment_id": payment.id,
                "amount": float(payment.amount),
                "verified_by": current_admin.id
            },
            country=payment.user.country,
            status="success"
        )
        
        db.add(activity)
        db.commit()
        
        return {"message": "Payment verified and user activated"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify payment"
        )