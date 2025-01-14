from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: str
    name: str
    country: str
    phone: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None

class UserLogin(BaseModel):
    email: str
    password: str

class User(UserBase):
    id: int
    is_active: bool = True
    is_verified: bool = False
    balance: float = 0.0

    class Config:
        from_attributes = True  # Allows ORM model conversion

class TokenResponse(BaseModel):
    token: str
    token_type: str
    user: User 

class TokenPayload(BaseModel):
    sub: Optional[int] = None
    email: str
    type: str
    payment_status: Optional[str] = None 