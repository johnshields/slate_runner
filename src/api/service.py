from datetime import datetime, timezone
from fastapi import FastAPI


def status_payload(app: FastAPI) -> dict:
    now = datetime.now(timezone.utc)
    started = getattr(app.state, "started_at", now)
    uptime_seconds = (now - started).total_seconds()

    return {
        "ok": True,
        "service": "slate_runner_api",
        "version": app.version if hasattr(app, "version") else "0.0.1",
        "timestamp": now.isoformat(),
        "uptime_seconds": int(uptime_seconds),
        "message": "RESTful API for fixing it in post.",
    }
