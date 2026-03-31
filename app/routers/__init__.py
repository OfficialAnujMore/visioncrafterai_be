"""
Routers package - Contains all API endpoints
"""

from .auth import router as auth_router
from .project import router as project_router

__all__ = ["auth_router", "project_router"]