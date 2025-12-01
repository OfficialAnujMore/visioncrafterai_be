from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database connection URL
    DATABASE_URL: str = (
        "postgresql+asyncpg://user:password@localhost:5432/visioncrafter"
    )

    # JWT Configuration
    JWT_SECRET_KEY: str = "VisionCrafterSecretKey"  # Secret key for JWT
    ALGORITHM: str = "HS256"  # JWT signing algorithm
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Token expiry time in minutes

    # App Configuration
    APP_NAME: str = "VisionCrafterAI"
    DEBUG: bool = True

    class Config:
        env_file = ".env"  # This means it will try to load from .env file
        case_sensitive = True


# Create a global settings object that we'll import everywhere
settings = Settings()
