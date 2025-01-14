from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any
import logging

from app.schemas.token import TokenResponse, UserLogin, PaymentVerificationRequest, PaymentVerificationResponse
from app.schemas.user import User, UserCreate
from app.api import deps
from app.core import security
from app.core.auth import get_current_user
from app import crud
from app.models.user import User as UserModel
from app.services.paystack import paystack
from app.models.payment import Payment
from app.models.transaction import Transaction
from app.services.notification_service import create_notification

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/register", response_model=TokenResponse)
def register(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
) -> Any:
    """
    Register new user and initiate payment flow.
    """
    try:
        logger.info(f"Registration attempt for email: {user_in.email}")
        
        # Check if user exists (email)
        user = crud.user.get_by_email(db, email=user_in.email)
        if user:
            if not user.is_verified:  # If user exists but hasn't paid
                return {
                    "access_token": security.create_access_token(data={
                        "sub": str(user.id),
                        "email": user.email,
                        "type": "access",
                        "payment_status": "pending"
                    }),
                    "token_type": "bearer",
                    "user": user,
                    "redirect_to": "/payment"
                }
            logger.warning(f"Email already exists and verified: {user_in.email}")
            raise HTTPException(
                status_code=409,
                detail="Email already registered and verified"
            )
            
        # Check if phone exists
        user = crud.user.get_by_phone(db, phone=user_in.phone)
        if user:
            logger.warning(f"Phone already exists: {user_in.phone}")
            raise HTTPException(
                status_code=409,
                detail="Phone number already registered"
            )
        
        logger.info(f"Creating new user with email: {user_in.email}")
        user = crud.user.create(db, obj_in=user_in)
        logger.info(f"User created successfully: {user.id}")
        
        # Create token payload with payment_status
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "type": "access",
            "payment_status": "pending"
        }
        
        access_token = security.create_access_token(data=token_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user,
            "redirect_to": "/payment"
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/login", response_model=TokenResponse)
async def login(
    user_data: UserLogin,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Login for access token.
    """
    try:
        logger.info(f"Login attempt for email: {user_data.email}")
        user = crud.user.authenticate(
            db, email=user_data.email, password=user_data.password
        )
        if not user:
            logger.warning(f"Invalid credentials for email: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        elif not crud.user.is_active(user):
            logger.warning(f"Inactive user attempted login: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )

        # Create token payload with payment_status and ensure ID is string
        token_data = {
            "sub": str(user.id),  # Explicitly convert to string
            "email": user.email,
            "type": "access",
            "payment_status": user.payment_status
        }
        
        access_token = security.create_access_token(data=token_data)
        
        # Log successful login
        logger.info(f"Successful login for user: {user.email}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user,
            "redirect_to": None if user.is_verified else "/payment"
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.get("/me", response_model=User)
def read_current_user(
    current_user: UserModel = Depends(get_current_user)
) -> Any:
    """
    Get current user.
    """
    return current_user 

@router.post("/verify-payment", response_model=PaymentVerificationResponse)
async def verify_payment(
    request: PaymentVerificationRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Verify payment and activate user account"""
    try:
        logger.info(f"Starting payment verification for user {current_user.email}")
        logger.info(f"Reference: {request.reference}")

        # Get fresh user instance from database
        db_user = crud.user.get(db, id=current_user.id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        # First verify with Paystack outside transaction
        try:
            payment_data = await paystack.verify_transaction(request.reference)
            logger.info(f"Payment verification successful: {payment_data}")
            
            # Validate payment data
            if not payment_data.get('status'):
                raise HTTPException(
                    status_code=400,
                    detail="Payment verification failed"
                )

            if payment_data.get('data', {}).get('status') != 'success':
                raise HTTPException(
                    status_code=400,
                    detail="Payment not successful"
                )

            # Now handle database updates in a single transaction
            try:
                # Create payment record
                payment = Payment(
                    user_id=db_user.id,
                    amount=payment_data['data']['amount'] / 100,  # Convert from kobo/pesewas
                    currency=payment_data['data']['currency'],
                    reference=request.reference,
                    status='success',
                    payment_method=payment_data['data'].get('channel', 'unknown'),
                    payment_data=payment_data['data'],
                    type='registration'  # Add payment type
                )
                db.add(payment)

                # Update user status
                db_user.is_verified = True
                db_user.payment_status = "completed"
                db_user.payment_reference = request.reference
                db.add(db_user)

                # Create transaction record
                transaction = Transaction(
                    user_id=db_user.id,
                    type="registration_payment",
                    amount=payment_data['data']['amount'] / 100,  # Convert from kobo/pesewas
                    status="completed",
                    payment_reference=request.reference,
                    payment_method=payment_data['data'].get('channel', 'unknown')
                )
                db.add(transaction)

                # Create notification
                notification = create_notification(
                    db=db,
                    user_id=db_user.id,
                    title="Payment Successful",
                    message=f"Your registration payment of {payment_data['data']['currency']} {payment_data['data']['amount'] / 100} was successful.",
                    type="payment",
                    metadata={
                        "amount": payment_data['data']['amount'] / 100,
                        "currency": payment_data['data']['currency'],
                        "reference": request.reference,
                        "payment_method": payment_data['data'].get('channel', 'unknown')
                    }
                )
                db.add(notification)

                # Commit all changes in one transaction
                db.commit()
                db.refresh(db_user)

                logger.info(f"Payment verification completed successfully for user {db_user.id}")

                return PaymentVerificationResponse(
                    success=True,
                    message="Payment verified successfully",
                    redirect="/dashboard",
                    user={
                        "id": db_user.id,
                        "email": db_user.email,
                        "is_verified": True,
                        "payment_status": "completed"
                    }
                )

            except Exception as db_error:
                db.rollback()
                logger.error(f"Database error: {str(db_error)}")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to update payment records"
                )

        except Exception as e:
            logger.error(f"Payment verification failed: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )