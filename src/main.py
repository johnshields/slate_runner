import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from config import settings
from api.routes import router as api_router


@asynccontextmanager
async def lifespan(api: FastAPI):
    api.state.started_at = datetime.now(timezone.utc)
    app.state.settings = settings
    print("[info]: slate_runner_api booting up...")
    yield
    print("[info]: slate_runner_api shutting down...")


def create_app() -> FastAPI:
    api = FastAPI(
        title="slate_runner_api",
        version="0.0.1",
        description="RESTful API for fixing it in post.",
        lifespan=lifespan,
    )

    # Root endpoint
    from fastapi.responses import HTMLResponse
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
    api.include_router(api_router, prefix="/api", tags=["api"])
    app.include_router(api_router, prefix="/api/v1", tags=["v1"])
    return api


app = create_app()
