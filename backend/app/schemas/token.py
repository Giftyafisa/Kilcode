from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.schemas.user import User

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    sub: Optional[str] = None
    email: str
    type: str
    payment_status: Optional[str] = None

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    email: str
    type: str
    payment_status: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: User
    redirect_to: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class PaymentVerificationRequest(BaseModel):
    reference: str
    trans: Optional[str] = None
    status: Optional[str] = None
    message: Optional[str] = None
    transaction: Optional[str] = None

class PaymentVerificationResponse(BaseModel):
    success: bool
    message: str
    redirect: Optional[str]
    user: Dict[str, Any] 