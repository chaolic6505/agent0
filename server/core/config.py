"""
Configuration settings for the auction system.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""

    # Database settings
    database_url: str = Field(..., env="DATABASE_URL")

    # Redis settings
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")

    # Application settings
    debug: bool = Field(default=False, env="DEBUG")

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env


# Global settings instance
settings = Settings()


def get_database_url() -> str:
    """Get database URL."""
    return settings.database_url


def get_redis_url() -> str:
    """Get Redis URL."""
    return settings.redis_url

