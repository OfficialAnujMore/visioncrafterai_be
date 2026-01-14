from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database connection URL
    DATABASE_URL: str

    # JWT Configuration
    JWT_SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    # Google OAuth Configuration
    GOOGLE_CLIENT_ID: str

    # App Configuration
    APP_NAME: str
    DEBUG: bool

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


# Create a global settings object that we'll import everywhere
settings = Settings()
