from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class PaymentBase(BaseModel):
    amount: float = Field(..., gt=0)
    payment_method: str
    description: Optional[str] = None

class PaymentCreate(PaymentBase):
    user_id: int
    type: str = "withdrawal"
    status: str = "pending"
    reference: Optional[str] = None

class Payment(PaymentBase):
    id: int
    user_id: int
    type: str
    status: str
    reference: Optional[str] = None
    phone: Optional[str] = None
    note: Optional[str] = None
    created_at: datetime
    verified_at: Optional[datetime] = None
    verified_by: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class PaymentInitiation(BaseModel):
    amount: float = Field(..., gt=0)
    payment_method: str
    phone: Optional[str] = None
    description: Optional[str] = None
    type: str = "withdrawal"

class PaymentVerification(BaseModel):
    status: str = Field(..., description="Payment verification status (approved/rejected)")
    note: Optional[str] = None

class PaymentUpdate(BaseModel):
    status: str
    note: Optional[str] = None

class PaymentResponse(BaseModel):
    id: int
    user_id: int
    amount: float
    payment_method: str
    status: str
    reference: Optional[str] = None
    created_at: datetime
    verified_at: Optional[datetime] = None
    verified_by: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)