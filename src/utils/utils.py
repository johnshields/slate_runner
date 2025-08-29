import random
import string
from urllib.parse import quote_plus
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from src.config import settings


# Build db url for Supabase session pooler
def build_database_url() -> str:
    if not all([settings.DB_HOST, settings.DB_PORT, settings.DB_NAME, settings.DB_USER, settings.DB_PASSWORD]):
        raise RuntimeError("DB parts missing; set DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD in .env")

    pw = quote_plus(settings.DB_PASSWORD)
    sslmode = settings.DB_SSLMODE or "require"

    return (
        "postgresql+psycopg2://"
        f"{settings.DB_USER}:{pw}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        f"?sslmode={sslmode}"
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
