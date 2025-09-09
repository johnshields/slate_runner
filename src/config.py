from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import os
from typing import Literal

ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8049
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # Environment
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False

    # Database Configuration
    DATABASE_URL: str | None = None
    DB_HOST: str | None = None
    DB_PORT: int | None = 5432
    DB_NAME: str | None = None
    DB_USER: str | None = None
    DB_PASSWORD: str | None = None
    DB_SSLMODE: str | None = "require"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: list[str] = ["*"]

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds

    model_config = SettingsConfigDict(
        env_file=os.path.join(ROOT_DIR, ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    @field_validator("LOG_LEVEL", mode="before")
    def normalize_log_level(cls, v):
        if isinstance(v, str):
            return v.upper()
        return v

    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


settings = Settings()
