from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """
    Schema for user registration request
    (...) Means required field
    """

    full_name: str = Field(..., min_length=1, max_length=100)
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr  # EmailStr validates email format
    password: str = Field(..., min_length=8)


class UserLoginRequest(BaseModel):
    """
    Schema for user login request
    """

    email: str
    password: str


class UserResponse(BaseModel):
    """
    Schema for user response
    This is what we send back to the client (no password!)
    """

    id: int
    username: str
    email: str
    full_name: str
    is_active: bool
    created_at: datetime


class UserUpdateRequest(BaseModel):
    """
    Schema for updating user profile
    Note: username is immutable for security
    """

    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None


class TokenResponse(BaseModel):
    """
    Schema for login response
    Client receives token to use in future requests
    """

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
