"""
Pydantic schemas for user data.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
import re


class UserBase(BaseModel):
    """Base schema for user data."""
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for user creation."""
    password: str
    
    @validator("password")
    def password_strength(cls, v):
        """Validate password strength."""
        min_length = 8
        if len(v) < min_length:
            raise ValueError(f"Password must be at least {min_length} characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(BaseModel):
    """Schema for user update."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    
    @validator("password")
    def password_strength(cls, v):
        """Validate password strength if provided."""
        if v is None:
            return v
        min_length = 8
        if len(v) < min_length:
            raise ValueError(f"Password must be at least {min_length} characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserInDBBase(UserBase):
    """Base schema for user in database."""
    id: int
    
    class Config:
        orm_mode = True


class User(UserInDBBase):
    """Schema for user response."""
    pass


class UserInDB(UserInDBBase):
    """Schema for user in database."""
    hashed_password: str


class Token(BaseModel):
    """Schema for JWT token."""
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Schema for JWT token payload."""
    sub: Optional[int] = None