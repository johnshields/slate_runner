from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator
from src.config import settings


def build_database_url_from_parts() -> str:
    if not all([settings.DB_HOST, settings.DB_PORT, settings.DB_NAME, settings.DB_USER, settings.DB_PASSWORD]):
        raise RuntimeError("DB parts missing; set DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD in .env")

    pw = quote_plus(settings.DB_PASSWORD)
    sslmode = settings.DB_SSLMODE or "require"

    return (
        "postgresql+psycopg2://"
        f"{settings.DB_USER}:{pw}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        f"?sslmode={sslmode}"
    )


DATABASE_URL = build_database_url_from_parts()

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"sslmode": "require"},
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
