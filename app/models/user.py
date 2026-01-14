from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    """User model for Google OAuth authentication"""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    google_id: str = Field(unique=True, index=True)  # Google's unique user ID
    email: str = Field(unique=True, index=True)
    name: str
    picture: Optional[str] = None  # URL to user's Google profile picture
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    last_login: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
