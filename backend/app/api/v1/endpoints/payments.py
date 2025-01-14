from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Dict, Optional, Any
from datetime import datetime
import logging

from ....core.auth import get_current_user
from ....core.database import get_db
from ....core.websocket_manager import manager
from ....models.user import User
from ....models.payment import Payment
from ....models.transaction import Transaction
from ....schemas.payment import PaymentCreate, PaymentResponse, PaymentVerification, PaymentInitiation
from ....services.payments.paystack import paystack_service
from ....services.activity_service import activity_service

logger = logging.getLogger(__name__)
router = APIRouter()

# Country-specific payment configurations
PAYMENT_CONFIG = {
    "ghana": {
        "min_amount": 150,  # GH₵ 150
        "currency": "GHS",
        "methods": ["mtn_momo", "vodafone_cash", "airteltigo"],
        "phone_required": True,
        "phone_prefix": "+233",
        "phone_length": 9
    },
    "nigeria": {
        "min_amount": 16000,  # ₦ 16,000
        "currency": "NGN",
        "methods": ["paystack", "bank_transfer", "ussd"],
        "phone_required": False
    }
}

async def process_paystack_payment(
    payment: Payment,
    current_user,
    db: Session
) -> PaymentResponse:
    try:
        # Get country-specific configuration
        config = paystack_service.get_country_config(current_user.country)
        
        # Initialize Paystack payment
        payment_result = await paystack_service.initialize_payment(
            email=current_user.email,
            amount=payment.amount,
            currency=config["currency"],
            metadata={
                "payment_id": payment.id,
                "user_id": current_user.id,
                "payment_type": payment.type,
                "country": current_user.country
            }
        )

        # Update payment record with reference
        payment.reference = payment_result["reference"]
        payment.status = "pending"
        db.add(payment)
        db.commit()
        db.refresh(payment)

        # Create activity record
        await activity_service.create_activity(
            db=db,
            user_id=current_user.id,
            activity_type="payment_initiated",
            description=f"Initiated {config['currency']} {payment.amount} payment",
            metadata={
                "payment_id": payment.id,
                "amount": payment.amount,
                "currency": config["currency"],
                "reference": payment_result["reference"]
            },
            country=current_user.country,
            status="pending"
        )

        return PaymentResponse(
            status="pending",
            message="Payment initiated successfully",
            reference=payment_result["reference"],
            authorization_url=payment_result["authorization_url"],
            data={
                "currency": config["currency"],
                "amount": payment.amount,
                "channels": config["channels"]
            }
        )

    except Exception as e:
        payment.status = "failed"
        db.add(payment)
        db.commit()
        
        # Log failed payment attempt
        await activity_service.create_activity(
            db=db,
            user_id=current_user.id,
            activity_type="payment_failed",
            description=f"Payment initiation failed: {str(e)}",
            metadata={
                "payment_id": payment.id,
                "error": str(e)
            },
            country=current_user.country,
            status="failed"
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/registration", response_model=PaymentResponse)
async def initiate_registration_payment(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Initiate registration payment"""
    try:
        # Get country-specific configuration
        config = paystack_service.get_country_config(current_user.country)
        
        # Validate user hasn't already paid
        if current_user.is_verified:
            raise HTTPException(
                status_code=400,
                detail="User is already verified"
            )
        
        # Check for pending payments
        pending_payment = db.query(Payment).filter(
            Payment.user_id == current_user.id,
            Payment.type == "registration",
            Payment.status == "pending"
        ).first()
        
        if pending_payment:
            return await process_paystack_payment(pending_payment, current_user, db)
        
        # Create payment record
        payment = Payment(
            user_id=current_user.id,
            amount=config["registration_fee"],
            type="registration",
            method="paystack",
            status="initiated",
            currency=config["currency"]
        )
        
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        return await process_paystack_payment(payment, current_user, db)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/verify", response_model=Dict)
async def verify_payment(
    verification: PaymentVerification,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify Paystack payment"""
    try:
        # Verify payment with Paystack
        payment_data = await paystack_service.verify_payment(verification.reference)
        
        # Get payment record
        payment = db.query(Payment).filter(
            Payment.reference == verification.reference,
            Payment.user_id == current_user.id
        ).first()
        
        if not payment:
            raise HTTPException(
                status_code=404,
                detail="Payment not found"
            )
            
        # Update payment status
        payment.status = payment_data["status"]
        payment.verified_at = payment_data["paid_at"]
        
        # If this is a registration payment and it's successful
        if payment.type == "registration" and payment_data["status"] == "success":
            current_user.is_verified = True
            
            # Create activity record
            await activity_service.create_activity(
                db=db,
                user_id=current_user.id,
                activity_type="registration_completed",
                description="Registration payment verified successfully",
                metadata={
                    "payment_id": payment.id,
                    "amount": payment_data["amount"],
                    "currency": payment_data["currency"],
                    "payment_method": payment_data["channel"]
                },
                country=current_user.country,
                status="success"
            )
            
            # Notify country admin
            await manager.notify_country_admin(
                current_user.country,
                {
                    "type": "new_user_verified",
                    "data": {
                        "user_id": current_user.id,
                        "email": current_user.email,
                        "payment_id": payment.id
                    }
                }
            )
        
        db.add(payment)
        db.add(current_user)
        db.commit()
        
        return {
            "status": "success",
            "data": {
                "payment_status": payment_data["status"],
                "amount": payment_data["amount"],
                "currency": payment_data["currency"],
                "is_verified": current_user.is_verified,
                "redirect_to": "/dashboard" if current_user.is_verified else None
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/config/{country}")
async def get_payment_config(country: str):
    """Get country-specific payment configuration"""
    return paystack_service.get_country_config(country)

@router.get("/health")
async def check_payment_health():
    """Check if payment service is healthy"""
    return await paystack_service.check_health()

@router.post("/test-flow")
async def test_payment_flow(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test the complete payment flow"""
    return await paystack_service.test_payment_flow(
        email=current_user.email,
        country=current_user.country
    )

@router.get("/analytics")
async def get_payment_analytics(
    country: str,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user = Depends(get_current_user)
):
    """Get payment analytics for a specific country"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access payment analytics"
        )
    
    return await paystack_service.get_payment_analytics(
        country=country,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/receipt/{reference}")
async def get_payment_receipt(
    reference: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate receipt for a payment"""
    # Get payment record
    payment = db.query(Payment).filter(
        Payment.reference == reference
    ).first()
    
    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )
    
    # Check if user is authorized to access this receipt
    if not current_user.is_admin and payment.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this receipt"
        )
    
    # Get payment data from Paystack
    payment_data = await paystack_service.verify_payment(reference)
    
    # Generate receipt
    return await paystack_service.generate_receipt(payment_data)

@router.post("/retry/{reference}")
async def retry_payment(
    reference: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retry a failed payment"""
    # Get payment record
    payment = db.query(Payment).filter(
        Payment.reference == reference
    ).first()
    
    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )
    
    # Check if user is authorized to retry this payment
    if not current_user.is_admin and payment.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to retry this payment"
        )
    
    # Only retry failed or abandoned payments
    if payment.status not in ["failed", "abandoned"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot retry payment with status: {payment.status}"
        )
    
    return await paystack_service.retry_payment(reference)

@router.post("/run-tests")
async def run_payment_tests(
    current_user = Depends(get_current_user)
):
    """Run comprehensive payment tests"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Only admins can run payment tests"
        )
    
    return await paystack_service.run_payment_tests(
        email=current_user.email,
        country=current_user.country
    )

@router.post("/initiate", response_model=PaymentResponse)
async def initiate_payment(
    payment_data: PaymentInitiation,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Initiate a withdrawal payment"""
    try:
        # Get country-specific configuration
        country_config = PAYMENT_CONFIG.get(current_user.country.lower())
        if not country_config:
            raise HTTPException(
                status_code=422,
                detail=f"Unsupported country: {current_user.country}"
            )

        # Validate amount
        if payment_data.amount < country_config["min_amount"]:
            raise HTTPException(
                status_code=422,
                detail=f"Minimum withdrawal amount is {country_config['currency']} {country_config['min_amount']}"
            )

        # Validate payment method
        if payment_data.payment_method not in country_config["methods"]:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid payment method for {current_user.country}. Supported methods: {', '.join(country_config['methods'])}"
            )

        # Validate phone number for mobile money methods
        if country_config["phone_required"] and payment_data.payment_method in ["mtn_momo", "vodafone_cash", "airteltigo"]:
            if not payment_data.phone:
                raise HTTPException(
                    status_code=422,
                    detail="Phone number is required for mobile money payments"
                )
            
            # Clean and validate phone number
            clean_phone = payment_data.phone.replace(country_config["phone_prefix"], "").replace("+", "")
            if len(clean_phone) != country_config["phone_length"]:
                raise HTTPException(
                    status_code=422,
                    detail=f"Invalid phone number format. Must be {country_config['phone_length']} digits"
                )

        # Check user balance
        if payment_data.amount > current_user.balance:
            raise HTTPException(
                status_code=422,
                detail="Insufficient balance"
            )

        # Create payment record
        payment = Payment(
            user_id=current_user.id,
            amount=payment_data.amount,
            payment_method=payment_data.payment_method,
            type="withdrawal",
            status="pending",
            currency=country_config["currency"],
            phone=payment_data.phone if country_config["phone_required"] else None,
            reference=f"WD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{current_user.id}"
        )
        
        db.add(payment)
        db.commit()
        db.refresh(payment)

        # Create transaction record
        transaction = Transaction(
            user_id=current_user.id,
            type="withdrawal",
            amount=payment_data.amount,
            status="pending",
            payment_method=payment_data.payment_method,
            payment_reference=payment.reference,
            currency=country_config["currency"],
            description=payment_data.description or "Withdrawal request"
        )

        db.add(transaction)
        db.commit()

        # Notify country admin about new withdrawal request
        await manager.notify_country_admin(
            current_user.country,
            {
                "type": "new_withdrawal_request",
                "data": {
                    "payment_id": payment.id,
                    "user_id": current_user.id,
                    "amount": float(payment.amount),
                    "currency": payment.currency,
                    "method": payment.payment_method
                }
            }
        )

        return PaymentResponse(
            id=payment.id,
            user_id=current_user.id,
            amount=float(payment.amount),
            payment_method=payment.payment_method,
            status="pending",
            reference=payment.reference,
            created_at=payment.created_at
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Payment initiation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to initiate payment"
        )

@router.post("/verify/{payment_id}", response_model=Dict[str, Any])
async def verify_payment(
    payment_id: int,
    verification: PaymentVerification,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify a payment status"""
    try:
        payment = db.query(Payment).filter(
            Payment.id == payment_id,
            Payment.user_id == current_user.id
        ).first()

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )

        # Get associated transaction
        transaction = db.query(Transaction).filter(
            Transaction.payment_reference == payment.reference,
            Transaction.user_id == current_user.id
        ).first()

        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )

        return {
            "status": payment.status,
            "message": "Payment status retrieved successfully",
            "data": {
                "payment_id": payment.id,
                "amount": payment.amount,
                "status": payment.status,
                "created_at": payment.created_at,
                "verified_at": payment.verified_at
            }
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Payment verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )