"""
Application Configuration

Uses Pydantic Settings for environment-based configuration.
Set APP_ENV=dev or APP_ENV=prod to switch modes.
"""

import os
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # Environment
    APP_ENV: Literal["dev", "prod"] = "dev"
    
    # Database
    DATABASE_URL: str = "sqlite:///./dev.db"
    
    # RabbitMQ
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672//"
    
    # LLM API Keys
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    
    # Worker Configuration
    MAX_WORKERS: int = 5
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.APP_ENV == "prod"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.APP_ENV == "dev"
    
    @property
    def database_url(self) -> str:
        """Get database URL, ensuring SQLite uses correct path."""
        if self.DATABASE_URL.startswith("sqlite"):
            # Ensure absolute path for SQLite
            return self.DATABASE_URL
        return self.DATABASE_URL


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience access
settings = get_settings()
