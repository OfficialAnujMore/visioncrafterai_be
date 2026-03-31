from pydantic_settings import BaseSettings


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
    CORS_ALLOW_ORIGINS: str = "http://localhost:5173,https://vision-crafter-ai.netlify.app"

    # Startup behavior
    DB_CREATE_TABLES_ON_STARTUP: bool = False
    DB_FAIL_FAST_ON_STARTUP_ERROR: bool = False

    @property
    def cors_allow_origins(self) -> list[str]:
        """Parse comma-separated CORS origins from environment."""
        return [origin.strip() for origin in self.CORS_ALLOW_ORIGINS.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


# Create a global settings object that we'll import everywhere
settings = Settings()
