#!/usr/bin/env python
import sys, os
from sqlalchemy import text
from src.db.db import engine
from src.config import settings

SRC_DIR = os.path.join(os.path.dirname(__file__), os.pardir, "src")
sys.path.insert(0, os.path.abspath(SRC_DIR))


def main() -> int:
    print(f"Using DB host: {settings.DB_HOST}, port: {settings.DB_PORT}, db: {settings.DB_NAME}")
    print(f"User: {settings.DB_USER}, SSL: {settings.DB_SSLMODE}")
    try:
        with engine.connect() as conn:
            row = conn.execute(text("select version(), now()")).fetchone()
            print("Connected OK.")
            print("version:", row[0])
            print("now():  ", row[1])
        return 0
    except Exception as e:
        print("Connection failed:", e)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
