import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from sqlalchemy import text
from config import settings
from api import router as api_router
from api.routes_v1 import router as v1_router
from db.db import engine
from logging_config import setup_logging, get_logger
from health import get_health_status, get_simple_health
from exceptions import handle_slate_runner_exception, SlateRunnerException
from middleware import RateLimitMiddleware, SecurityHeadersMiddleware, RequestLoggingMiddleware


@asynccontextmanager
async def lifespan(api: FastAPI):
    # Setup logging first
    setup_logging()
    logger = get_logger(__name__)

    api.state.started_at = datetime.now(timezone.utc)
    api.state.settings = settings
    logger.info("slate_runner_api booting up...")

    # Get DB connection up and ready.
    try:
        with engine.connect() as conn:
            ts = conn.execute(text("select now()")).scalar_one()
            logger.info(f"database ready @ {ts.isoformat()}")
    except Exception as e:
        logger.error(f"database connection failed on startup: {e}")
        if os.getenv("CI") != "true":
            raise

    try:
        yield
    finally:
        engine.dispose()
        logger.info("slate_runner_api shutting down...")


# Init FastAPI
def create_app() -> FastAPI:
    api = FastAPI(
        title="slate_runner_api",
        version="0.0.1",
        description="RESTful FastAPI for fixing it in post.",
        lifespan=lifespan,
    )

    # Add middleware in order (last added is outermost)
    api.add_middleware(SecurityHeadersMiddleware)
    api.add_middleware(RequestLoggingMiddleware)
    api.add_middleware(RateLimitMiddleware)
    api.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
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
            <p><strong>RESTful FastAPI for fixing it in post.</strong></p>
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

    # Enhanced health check endpoints
    @api.get("/health", tags=["health"])
    def health_check():
        """Comprehensive health check"""
        return get_health_status()

    @api.get("/health/simple", tags=["health"])
    def simple_health_check():
        """Simple health check for load balancers"""
        return get_simple_health()

    # Exception handlers
    @api.exception_handler(SlateRunnerException)
    async def slate_runner_exception_handler(request: Request, exc: SlateRunnerException):
        return JSONResponse(
            status_code=400,
            content=handle_slate_runner_exception(exc).detail
        )

    @api.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "message": "Validation error",
                "details": exc.errors()
            }
        )

    # Include API routes
    api.include_router(api_router, prefix="/api")
    api.include_router(v1_router, prefix="/api/v1")
    return api


app = create_app()
