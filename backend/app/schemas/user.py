from datetime import datetime

from pydantic import BaseModel, field_validator

from app.models.user import UserRole


class UserCreate(BaseModel):
    phone: str
    name: str
    password: str
    address_cuba: str | None = None
    province_cuba: str | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        cleaned = v.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if not cleaned.lstrip("+").isdigit():
            raise ValueError("Phone number must contain only digits and optional leading +")
        if len(cleaned.lstrip("+")) < 7:
            raise ValueError("Phone number too short")
        return cleaned

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class UserLogin(BaseModel):
    phone: str
    password: str


class UserRead(BaseModel):
    id: int
    phone: str
    name: str
    role: UserRole
    address_cuba: str | None
    province_cuba: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    name: str | None = None
    address_cuba: str | None = None
    province_cuba: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserRead
