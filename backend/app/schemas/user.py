from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    cuba_address: Optional[str] = None
    cuba_city: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: str
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    cuba_address: Optional[str] = None
    cuba_city: Optional[str] = None
