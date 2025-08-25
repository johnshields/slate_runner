from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator
from utils.utils import build_database_url


# Create the engine and session factory
def setup_database():
    db_url = build_database_url()
    db_engine = create_engine(
        db_url,
        pool_pre_ping=True,
        connect_args={"sslmode": "require"},
        future=True,
    )
    session_local = sessionmaker(bind=db_engine, autoflush=False, autocommit=False, future=True)
    return session_local, db_engine


# Instantiate at startup
SessionLocal, engine = setup_database()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
