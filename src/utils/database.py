from urllib.parse import quote_plus
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
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


def db_lookup(db: Session, model, identifier: str) -> object:
    """Lookup a database record by UID or name."""
    item = db.scalar(select(model).where(model.uid == identifier))
    if not item and hasattr(model, 'name'):
        item = db.scalar(select(model).where(model.name == identifier))

    if not item:
        raise HTTPException(
            status_code=404,
            detail=f"{model.__name__} with UID or name '{identifier}' not found."
        )
    return item

