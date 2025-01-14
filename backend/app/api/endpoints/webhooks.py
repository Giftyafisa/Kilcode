from fastapi import APIRouter, Request, HTTPException, Depends
from app.core.config import settings
from app.services.transaction_service import TransactionService
from app.db.session import get_db
from sqlalchemy.orm import Session
import hmac
import hashlib

router = APIRouter()

def verify_paystack_signature(signature: str, payload: bytes) -> bool:
    """Verify Paystack webhook signature"""
    computed = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode('utf-8'),
        payload,
        hashlib.sha512
    ).hexdigest()
    return hmac.compare_digest(computed, signature)

@router.post("/paystack")
async def paystack_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    signature = request.headers.get('x-paystack-signature')

    if not signature or not verify_paystack_signature(signature, payload):
        raise HTTPException(status_code=400, detail="Invalid signature")

    data = await request.json()
    event = data.get('event')
    
    if event == 'charge.success':
        reference = data['data']['reference']
        await TransactionService.update_transaction_status(
            db,
            reference,
            'completed',
            data['data']
        )
        return {"status": "success"}

@router.post("/mobile-money/{provider}")
async def mobile_money_webhook(
    provider: str,
    request: Request,
    db: Session = Depends(get_db)
):
    data = await request.json()
    
    # Verify provider-specific signatures
    if provider == 'mtn_momo':
        # MTN MoMo signature verification
        signature = request.headers.get('x-mtn-signature')
        if not verify_mtn_signature(signature, await request.body()):
            raise HTTPException(status_code=400, detail="Invalid signature")
    
    reference = data.get('reference')
    status = data.get('status')

    if status == 'successful':
        await TransactionService.update_transaction_status(
            db,
            reference,
            'completed',
            data
        )
    elif status in ['failed', 'cancelled']:
        await TransactionService.update_transaction_status(
            db,
            reference,
            'failed',
            data
        )

    return {"status": "success"} 