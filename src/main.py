import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from api.routes import router as api_router


@asynccontextmanager
async def lifespan(api: FastAPI):
    api.state.started_at = datetime.now(timezone.utc)
    print("[info]: slate_runner_api booting up...")
    yield
    print("[info]: slate_runner_api shutting down...")


def create_app() -> FastAPI:
    api = FastAPI(
        title="slate_runner_api",
        version="0.0.1",
        description="RESTful API for the visual effects world.",
        lifespan=lifespan,
    )

    # Root endpoint
    @api.get("/", tags=["root"])
    def root():
        return {
            "name": "slate_runner_api",
            "message": "Welcome. See /api/ for status.",
        }

    # Favicon route
    @api.get("/favicon.ico", include_in_schema=False)
    def favicon():
        file_path = os.path.join(os.path.dirname(__file__), "static", "favicon.ico")
        return FileResponse(file_path)

    # Mount all static files
    api.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

    # Include API routes
    api.include_router(api_router, prefix="/api", tags=["api"])
    return api


app = create_app()
