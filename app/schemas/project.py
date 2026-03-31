from datetime import datetime
from typing import Literal
from pydantic import BaseModel


class CreateProjectRequest(BaseModel):
    """Schema for creating a new project"""

    file_id: str
    user_id: int
    title: str
    project_url: str
    thumbnail_url: str
    width: int
    height: int
    file_type: Literal["video", "image"]
    canvas_state: dict | None = None


class ProjectResponse(BaseModel):
    """Schema for project response"""
    id: int
    file_id: str
    user_id: int
    title: str
    project_url: str
    thumbnail_url: str
    width: int
    height: int
    file_type: Literal["video", "image"]
    canvas_state: dict | None = None
    created_at: datetime
    updated_at: datetime


class UpdateProjectRequest(BaseModel):
    """Schema for updating a project"""

    title: str | None = None
    project_url: str | None = None
    thumbnail_url: str | None = None
    width: int | None = None
    height: int | None = None
    file_type: Literal["video", "image"] | None = None
    canvas_state: dict | None = None
