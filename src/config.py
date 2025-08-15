from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import os

ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    API_HOST: str
    API_PORT: int
    LOG_LEVEL: str

    DATABASE_URL: str | None = None
    DB_HOST: str | None = None
    DB_PORT: int | None = 5432
    DB_NAME: str | None = None
    DB_USER: str | None = None
    DB_PASSWORD: str | None = None
    DB_SSLMODE: str | None = "require"

    model_config = SettingsConfigDict(
        env_file=os.path.join(ROOT_DIR, ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
