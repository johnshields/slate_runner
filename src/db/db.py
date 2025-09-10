from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator
from utils.utils import build_database_url
from app.config import settings
from app.logging_config import get_logger

logger = get_logger(__name__)


# Create the engine and session factory
def setup_database():
    db_url = build_database_url()

    # Engine configuration
    engine_kwargs = {
        "pool_pre_ping": True,
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_recycle": 3600,  # Recycle connections after 1 hour
        "connect_args": {"sslmode": settings.DB_SSLMODE},
        "future": True,
    }

    if settings.is_development():
        engine_kwargs["echo"] = settings.DEBUG

    db_engine = create_engine(db_url, **engine_kwargs)
    session_local = sessionmaker(
        bind=db_engine,
        autoflush=False,
        autocommit=False,
        future=True
    )

    logger.info(
        f"Database engine configured with pool_size={settings.DB_POOL_SIZE}, max_overflow={settings.DB_MAX_OVERFLOW}")
    return session_local, db_engine


# Instantiate at startup
SessionLocal, engine = setup_database()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
