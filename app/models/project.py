from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING
import json

if TYPE_CHECKING:
    from .user import User


class FileType(str, Enum):
    """Enum for file types"""

    VIDEO = "video"
    IMAGE = "image"


class Project(SQLModel, table=True):
    """Project model for storing user-generated projects"""

    __tablename__ = "projects"

    id: int | None = Field(default=None, primary_key=True)
    file_id: str
    user_id: int = Field(foreign_key="user.id", index=True)
    title: str
    project_url: str
    thumbnail_url: str
    width: int
    height: int
    file_type: FileType
    canvas_state: str | None = Field(default=None, description="JSON serialized canvas state")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    # Relationship
    user: "User" = Relationship(back_populates="projects")
