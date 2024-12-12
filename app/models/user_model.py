from pydantic import field_validator, BaseModel
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field
from typing import Optional
import re


class UserBase(SQLModel):
    phone_number: str = Field(unique=True)
    role: Optional[str] = "user"

    @field_validator("phone_number")
    def validate_phone_number(cls, value):
        if not re.match(r"^09[0-9]{9}$", value):
            raise ValueError("Invalid phone number format")
        return value


class User(UserBase, table=True):
    id: int = Field(default=None, primary_key=True)
    otp: Optional[str] = None
    joined_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("otp")
    def validate_otp(cls, value):
        if value and not re.match(r"[0-9]{6}$", value):
            raise ValueError("Invalid OTP format")
        return value


class UserCreate(SQLModel):
    phone_number: str

    @field_validator("phone_number")
    def validate_phone_number(cls, value):
        if not re.match(r"^09[0-9]{9}$", value):
            raise ValueError("Invalid phone number format")
        return value


class UserPublic(SQLModel):
    id: int
    phone_number: str
    joined_date: datetime


class AdminUserPublic(UserPublic):
    role: str


class OTPRequest(SQLModel):
    phone_number: str


class UserLogin(OTPRequest):
    otp: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class UserUpdate(SQLModel):
    phone_number: Optional[str] = None
