"""
Routers package - Contains all API endpoints
"""

from .auth import router as auth_router

__all__ = ["auth_router"]