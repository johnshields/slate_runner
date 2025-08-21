import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from config import settings
from api import router as api_router
from api.routes_v1 import router as v1_router
from db.db import engine


@asynccontextmanager
async def lifespan(api: FastAPI):
    api.state.started_at = datetime.now(timezone.utc)
    api.state.settings = settings
    print("[info]: slate_runner_api booting up...")

    # Get DB connection up and ready.
    try:
        with engine.connect() as conn:
            ts = conn.execute(text("select now()")).scalar_one()
            print(f"[info]: database ready @ {ts.isoformat()}")
    except Exception as e:
        print(f"[error]: database connection failed on startup: {e}")
        if os.getenv("CI") != "true":
            raise

    try:
        yield
    finally:
        engine.dispose()
        print("[info]: slate_runner_api shutting down...")


# Init FastAPI
def create_app() -> FastAPI:
    api = FastAPI(
        title="slate_runner_api",
        version="0.0.1",
        description="RESTful API for fixing it in post.",
        lifespan=lifespan,
    )

    api.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Root endpoint
    @api.get("/", response_class=HTMLResponse, tags=["root"])
    def root():
        return """
        <html>
          <head>
            <link rel="icon" href="/favicon.ico" type="image/x-icon">
            <title>slate_runner</title>
          </head>
          <body style="font-family: ui-sans-serif, system-ui">
            <h1>slate_runner</h1>
            <p><strong>RESTful API for fixing it in post.</strong></p>
            <p>See <a href="/api/">/api/</a> for status or <a href="/docs">/docs</a> for OpenAPI.</p>
            <p>See <a href="https://kntn.ly/a573c361" target="_blank">GitHub Repo</a></p>
          </body>
        </html>
        """

    # Favicon route
    @api.get("/favicon.ico", include_in_schema=False)
    def favicon():
        file_path = os.path.join(os.path.dirname(__file__), "static", "favicon.ico")
        return FileResponse(file_path)

    # Mount all static files
    api.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

    # Include API routes
    api.include_router(api_router, prefix="/api")
    api.include_router(v1_router, prefix="/api/v1")
    return api


app = create_app()
