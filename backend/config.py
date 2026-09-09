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


settings = Settings()
