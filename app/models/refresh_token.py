from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field

class RefreshToken(SQLModel, table=True):
    """RefreshToken database model - stores refresh tokens for users"""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int= Field(foreign_key="user.id", index=True)
    token: str = Field(unique=True, index=True)  # The actual JWT token
    expires_at: datetime  # When this refresh token expires
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    is_revoked: bool = Field(default=False)  # For logout functionality