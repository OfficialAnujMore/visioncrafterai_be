from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Standard API success response"""
    success: bool = True
    message: Optional[str] = None
    data: T


class ApiErrorResponse(BaseModel):
    """Standard API error response"""
    success: bool = False
    message: str
    error: Optional[str] = None
    statusCode: Optional[int] = None
