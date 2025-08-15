#!/usr/bin/env python
from sqlalchemy import text
from db import engine
from config import settings


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
