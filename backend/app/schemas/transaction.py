from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class TransactionBase(BaseModel):
    type: str = Field(..., description="Type of transaction (withdrawal, deposit, etc.)")
    amount: float = Field(..., gt=0)
    fee: float = Field(default=0.0, ge=0)
    payment_method: str
    status: str = "pending"
    payment_reference: str
    description: Optional[str] = None
    currency: Optional[str] = None

class TransactionCreate(TransactionBase):
    user_id: int

class Transaction(TransactionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TransactionListResponse(BaseModel):
    transactions: List[Transaction]
    balance: float 