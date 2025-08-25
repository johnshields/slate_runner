from fastapi import FastAPI
from datetime import datetime, timezone
from sqlalchemy import text

from db.db import engine


def status_payload(app: FastAPI) -> dict:
    now = datetime.now(timezone.utc)
    started = getattr(app.state, "started_at", now)
    uptime_seconds = (now - started).total_seconds()

    return {
        "ok": True,
        "service": "slate_runner_api",
        "version": app.version if hasattr(app, "version") else "0.0.1",
        "api_version": "v1",
        "timestamp": now.isoformat(),
        "uptime_seconds": int(uptime_seconds),
        "message": "RESTful API for fixing it in post.",
    }


def db_conn() -> dict:
    try:
        with engine.connect() as conn:
            conn.execute(text("select 1"))
        return {"ok": True, "db": "ready"}
    except Exception as e:
        return {"ok": False, "db": f"error: {e.__class__.__name__}"}
