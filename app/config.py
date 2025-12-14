from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database connection URL
    DATABASE_URL: str

    # JWT Configuration (All required - no defaults)
    JWT_SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    # App Configuration
    APP_NAME: str
    DEBUG: bool

    class Config:
        env_file = ".env"  # This means it will try to load from .env file
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env that aren't defined here


# Create a global settings object that we'll import everywhere
settings = Settings()
