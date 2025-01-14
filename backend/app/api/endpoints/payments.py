from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.transaction import Transaction
from app.schemas.payment import PaymentVerification
from app.services.payment_service import PaymentService
from app.core.security import get_current_user
from typing import Dict

router = APIRouter()

@router.post("/verify/{payment_method}")
async def verify_payment(
    payment_method: str,
    verification: PaymentVerification,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    try:
        transaction = await PaymentService.verify_payment(
            db,
            payment_method,
            verification.reference,
            current_user
        )
        
        return {
            "status": "success",
            "data": {
                "transaction_id": transaction.id,
                "status": transaction.status,
                "amount": transaction.amount,
                "reference": transaction.payment_reference
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status/{reference}")
async def check_payment_status(
    reference: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    transaction = db.query(Transaction).filter(
        Transaction.payment_reference == reference,
        Transaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
        
    return {
        "status": "success",
        "data": {
            "transaction_id": transaction.id,
            "status": transaction.status,
            "amount": transaction.amount,
            "reference": transaction.payment_reference,
            "created_at": transaction.created_at,
            "completed_at": transaction.completed_at
        }
    } 