"""
config.py: Central application configuration for SKILLTRACE FastAPI backend.
"""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "SKILLTRACE"
    PROJECT_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database URI (defaults to SQLite; PostgreSQL connection string can be injected)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./skilltrace.db")

    # AI Configuration
    ENABLE_SEMANTIC_MATCHING: bool = os.getenv("ENABLE_SEMANTIC_MATCHING", "false").lower() == "true"
    SEMANTIC_SIMILARITY_THRESHOLD: float = float(os.getenv("SEMANTIC_SIMILARITY_THRESHOLD", "0.75"))

    # CORS
    CORS_ORIGINS: list[str] = ["*"]

    # Admin Portal Credentials
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")
    ADMIN_TOKEN: str = os.getenv("ADMIN_TOKEN", "skilltrace-admin-secret-token-2026")


settings = Settings()
