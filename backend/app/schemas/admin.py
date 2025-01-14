from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Literal
from datetime import datetime

# Define valid roles and countries
AdminRoles = Literal["admin", "super_admin", "code_analyst", "country_admin"]
Countries = Literal["ghana", "nigeria"]

class AdminBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    country: Countries
    role: AdminRoles = "admin"
    is_active: Optional[bool] = True

    @validator('role')
    def validate_role(cls, v, values):
        # Code analysts must have a country assigned
        if v == "code_analyst" and not values.get('country'):
            raise ValueError("Code analysts must have a country assigned")
        return v

class AdminCreate(AdminBase):
    password: str

class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class AdminUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None
    country: Optional[Countries] = None
    is_active: Optional[bool] = None

class AdminInDBBase(AdminBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class Admin(AdminInDBBase):
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class AdminInDB(AdminInDBBase):
    hashed_password: str

class AdminResponse(BaseModel):
    token: str
    email: str
    role: AdminRoles
    country: Countries
    full_name: Optional[str] = None
    id: int 