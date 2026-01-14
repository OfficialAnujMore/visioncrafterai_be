from datetime import datetime
from pydantic import BaseModel


class GoogleAuthRequest(BaseModel):
    """Schema for Google OAuth token verification request"""
    token: str  # Google ID token from frontend


class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    google_id: str
    email: str
    name: str
    picture: str | None
    is_active: bool
    created_at: datetime


class AuthResponse(BaseModel):
    """Schema for authentication response"""
    access_token: str
    token_type: str
    user: UserResponse
