import random
import string
from urllib.parse import quote_plus
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional, Type, TypeVar
from enum import Enum
from app.config import settings


def build_database_url() -> str:
    """Build PostgreSQL connection URL from environment variables."""
    required_fields = {
        "DB_HOST": settings.DB_HOST,
        "DB_PORT": settings.DB_PORT,
        "DB_NAME": settings.DB_NAME,
        "DB_USER": settings.DB_USER,
        "DB_PASSWORD": settings.DB_PASSWORD,
    }
    
    missing = [key for key, value in required_fields.items() if not value]
    if missing:
        raise RuntimeError(
            f"Missing required database configuration in .env: {', '.join(missing)}"
        )
    
    pw = quote_plus(settings.DB_PASSWORD)
    
    return (
        f"postgresql+psycopg2://{settings.DB_USER}:{pw}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        f"?sslmode={settings.DB_SSLMODE}"
    )


def generate_uid(prefix: str, length: int = 6) -> str:
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return f"{prefix}_{suffix}"


def db_lookup(db: Session, model, identifier: str) -> object:
    item = db.scalar(select(model).where(model.uid == identifier))
    if not item and hasattr(model, 'name'):
        item = db.scalar(select(model).where(model.name == identifier))

    if not item:
        raise HTTPException(
            status_code=404,
            detail=f"{model.__name__} with UID or name '{identifier}' not found."
        )
    return item


T = TypeVar("T", bound=Enum)


def normalize_input(value: Optional[str], enum_cls: Type[T]) -> Optional[T]:
    if value is None:
        return None

    for member in enum_cls:
        if member.value.lower() == value.lower():
            return member

    raise ValueError(f"Invalid Enum value: {value}. Must be one of {[m.value for m in enum_cls]}")
