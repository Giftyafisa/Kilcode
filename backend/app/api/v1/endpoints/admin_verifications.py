from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from ....core.database import get_db
from ....models.payment import Payment
from ....models.user import User
from ....models.transaction import Transaction
from ....schemas.payment import PaymentVerification, PaymentResponse
from ....core.security import get_current_admin
from ....core.websocket_manager import manager
from sqlalchemy.sql import func
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/pending", response_model=List[Dict[str, Any]])
async def get_pending_verifications(
    country: str,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get pending payment verifications for a country"""
    try:
        # Verify admin has access to this country
        if current_admin.country.lower() != country.lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized for this country"
            )
        
        # Get pending payments for the country
        pending_payments = db.query(Payment).join(User).filter(
            User.country == country,
            Payment.status == "pending",
            Payment.type == "withdrawal"  # Only get withdrawal requests
        ).all()
        
        # Format response
        response = []
        for payment in pending_payments:
            response.append({
                "id": payment.id,
                "user": {
                    "id": payment.user.id,
                    "name": payment.user.name,
                    "email": payment.user.email
                },
                "amount": float(payment.amount),
                "currency": "GHS" if country.lower() == "ghana" else "NGN",
                "method": payment.payment_method,
                "created_at": payment.created_at.isoformat(),
                "status": payment.status,
                "type": payment.type
            })
        
        return response

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error fetching pending verifications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch pending verifications"
        )

@router.post("/{payment_id}", response_model=Dict[str, Any])
async def verify_payment(
    payment_id: int,
    verification: PaymentVerification,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Verify a withdrawal payment"""
    try:
        # Get payment and associated user
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

        # Get associated transaction
        transaction = db.query(Transaction).filter(
            Transaction.payment_reference == payment.reference
        ).first()

        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Associated transaction not found"
            )
        
        # Update payment status
        payment.status = verification.status
        payment.verified_by = current_admin.id
        payment.verified_at = func.now()
        
        # Update transaction status
        transaction.status = verification.status
        
        # If payment is rejected, refund the amount to user's balance
        if verification.status == "rejected":
            payment.user.balance += payment.amount
        
        # Add verification note if provided
        if verification.note:
            payment.note = verification.note
        
        db.commit()
        
        # Notify user through WebSocket
        currency = "GHS" if payment.user.country.lower() == "ghana" else "NGN"
        await manager.notify_user(
            payment.user.email,
            {
                "type": "payment_verification",
                "data": {
                    "payment_id": payment.id,
                    "status": verification.status,
                    "amount": float(payment.amount),
                    "currency": currency,
                    "new_balance": float(payment.user.balance)
                }
            }
        )
        
        return {
            "message": f"Payment {verification.status}",
            "payment_id": payment_id,
            "user_id": payment.user_id,
            "status": payment.status,
            "amount": float(payment.amount),
            "currency": currency
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error verifying payment: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify payment"
        ) 