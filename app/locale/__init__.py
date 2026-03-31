"""
Localization module for VisionCrafterAI Backend API
Provides centralized message management for API responses
"""

from .en import (
    AUTH_MESSAGES,
    USER_MESSAGES,
    VALIDATION_MESSAGES,
    HTTP_MESSAGES,
    DATABASE_MESSAGES,
    GENERAL_MESSAGES,
    get_message,
)

__all__ = [
    'AUTH_MESSAGES',
    'USER_MESSAGES',
    'VALIDATION_MESSAGES',
    'HTTP_MESSAGES',
    'DATABASE_MESSAGES',
    'GENERAL_MESSAGES',
    'get_message',
]
