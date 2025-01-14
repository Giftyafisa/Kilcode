from pydantic import BaseModel, EmailStr
from typing import Optional, Literal

class UserBase(BaseModel):
    email: EmailStr
    name: str
    country: str
    phone: str

class UserCreate(UserBase):
    password: str

class UserStatusUpdate(BaseModel):
    """Schema for updating user status"""
    status: Literal["active", "suspended", "pending"]

class UserUpdate(BaseModel):
    """Schema for updating user data"""
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    payment_status: Optional[str] = None
    payment_reference: Optional[str] = None
    balance: Optional[float] = None
    status: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    payment_status: str
    balance: float
    payment_reference: Optional[str] = None
    status: str = "active"

    class Config:
        from_attributes = True

class UserInDB(User):
    hashed_password: str 