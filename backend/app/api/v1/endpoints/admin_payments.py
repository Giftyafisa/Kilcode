from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime, timedelta
from sqlalchemy import func
import logging

from ....core.auth import get_current_admin
from ....core.database import get_db
from ....core.websocket_manager import manager
from ....models.payment import Payment
from ....models.user import User
from ....schemas.payment import PaymentResponse, PaymentVerification
from ....models.transaction import Transaction
from ....models.admin import Admin

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/withdrawals/pending")
async def get_pending_withdrawals(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get pending withdrawal requests for admin's country"""
    try:
        country = current_admin.country.lower()
        logger.info(f"Fetching pending withdrawals for {country}")
        
        query = db.query(
            Payment.id,
            Payment.amount,
            Payment.payment_method,
            Payment.status,
            Payment.created_at,
            Payment.phone,
            User.name.label('user_name'),
            User.email.label('user_email'),
            User.id.label('user_id')
        ).join(User).filter(
            func.lower(User.country) == country,
            Payment.type == 'withdrawal',
            Payment.status == 'pending'
        )
        
        payments = query.order_by(Payment.created_at.desc()).all()
        
        logger.info(f"Found {len(payments)} pending withdrawals")
        
        return [{
            "id": payment.id,
            "user_id": payment.user_id,
            "user_name": payment.user_name,
            "user_email": payment.user_email,
            "amount": payment.amount,
            "payment_method": payment.payment_method,
            "status": payment.status,
            "created_at": payment.created_at,
            "phone": payment.phone
        } for payment in payments]
        
    except Exception as e:
        logger.error(f"Error fetching pending withdrawals: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch pending withdrawals: {str(e)}"
        )

@router.get("/statistics")
async def get_payment_statistics(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get payment statistics for admin's country"""
    try:
        country = current_admin.country.lower()
        logger.info(f"Fetching payment statistics for {country}")
        
        # Get payments from the last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        # Base query for withdrawals in admin's country
        base_query = db.query(Payment).join(User).filter(
            func.lower(User.country) == country,
            Payment.type == 'withdrawal',
            Payment.created_at >= thirty_days_ago
        )
        
        # Get total payments
        total_payments = base_query.count()
        
        # Get pending payments
        pending_payments = base_query.filter(Payment.status == 'pending').count()
        
        # Get approved payments
        approved_payments = base_query.filter(Payment.status == 'approved').count()
        
        # Get rejected payments
        rejected_payments = base_query.filter(Payment.status == 'rejected').count()
        
        # Get total amount
        total_amount = db.query(func.sum(Payment.amount)).select_from(Payment).join(User).filter(
            func.lower(User.country) == country,
            Payment.type == 'withdrawal',
            Payment.status == 'approved'
        ).scalar() or 0
        
        return {
            "totalPayments": total_payments,
            "pendingPayments": pending_payments,
            "approvedPayments": approved_payments,
            "rejectedPayments": rejected_payments,
            "totalAmount": float(total_amount)
        }
        
    except Exception as e:
        logger.error(f"Error fetching payment statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch payment statistics: {str(e)}"
        )

@router.post("/{payment_id}/verify")
async def verify_payment(
    payment_id: int,
    verification: PaymentVerification,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Verify a withdrawal request"""
    try:
        # Get payment with user info
        payment = db.query(Payment, User).join(User).filter(
            Payment.id == payment_id
        ).first()
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
            
        payment, user = payment
        
        # Verify admin has access to this country
        if current_admin.country.lower() != user.country.lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to verify payments for this country"
            )
            
        # Update payment status
        payment.status = verification.status
        payment.verified_by = current_admin.id
        payment.verified_at = func.now()
        
        if verification.note:
            payment.note = verification.note
            
        # If payment is approved, update user's balance
        if verification.status == 'approved':
            # Check if user has sufficient balance
            if user.balance < payment.amount:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Insufficient balance"
                )
                
            # Deduct from user's balance
            old_balance = user.balance
            user.balance -= payment.amount
            
            logger.info(f"=== BALANCE UPDATE ===")
            logger.info(f"User: {user.email}")
            logger.info(f"Old balance: {old_balance}")
            logger.info(f"Withdrawal amount: {payment.amount}")
            logger.info(f"New balance: {user.balance}")
            
            # Create transaction record
            transaction = Transaction(
                user_id=user.id,
                type='withdrawal',
                amount=payment.amount,
                fee=0.0,
                status='completed',
                payment_method=payment.payment_method,
                payment_reference=f'WD-{payment.id}',
                description=f'Withdrawal request approved',
                currency='NGN' if user.country.lower() == 'nigeria' else 'GHS'
            )
            db.add(transaction)
            
            logger.info(f"=== TRANSACTION CREATED ===")
            logger.info(f"Transaction type: withdrawal")
            logger.info(f"Transaction amount: {payment.amount}")
            logger.info(f"Transaction status: completed")
            
        try:
            db.commit()
            logger.info(f"Payment {payment_id} verified as {verification.status}")
            
            # Notify user through WebSocket
            await manager.notify_payment_verification(user.email, {
                "payment_id": payment.id,
                "status": verification.status,
                "note": verification.note,
                "amount": payment.amount,
                "new_balance": user.balance if verification.status == 'approved' else None
            })
            
            return {
                "message": "Payment verified successfully",
                "status": verification.status,
                "new_balance": user.balance if verification.status == 'approved' else None
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error committing payment verification: {str(e)}")
            raise
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify payment: {str(e)}"
        ) 