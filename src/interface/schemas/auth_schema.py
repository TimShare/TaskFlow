from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class UserCreate(BaseModel):
    username: str = Field(..., example="user1")
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., min_length=6, example="password123")


class UserRead(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    is_active: bool
    is_superuser: bool
    scopes: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., example="password123")


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
