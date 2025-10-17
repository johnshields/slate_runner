import logging
import sys
from pathlib import Path
from app.config import settings

LOGS_DIR = Path(__file__).parent.parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# ANSI color codes
COLORS = {
    "debug": "\033[2m",  # green
    "info": "\033[34m",  # blue
    "warning": "\033[93m",  # yellow
    "error": "\033[91m",  # red
    "critical": "\033[1;91m",  # bold + red
    "reset": "\033[0m"
}


class ColorFormatter(logging.Formatter):
    """Formatter that lowercases levelname and adds colors."""

    def format(self, record):
        level = record.levelname.lower()
        record.levelname = level
        color = COLORS.get(level, COLORS["reset"])
        message = super().format(record)
        return f"{color}{message}{COLORS['reset']}"


def setup_logging():
    """Configure application logging"""

    # Console formatter - simple and clean
    console_formatter = ColorFormatter('[%(levelname)s]: %(message)s')

    # File formatter - keep detailed for debugging
    file_format = '[%(levelname)s]: %(message)s @ %(asctime)s - %(name)s - %(filename)s:%(lineno)d'

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))

    # Clear old handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File formatter
    file_formatter = logging.Formatter(file_format)
    file_handler = logging.FileHandler(LOGS_DIR / "slate_runner.log")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    error_handler = logging.FileHandler(LOGS_DIR / "errors.log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    root_logger.addHandler(error_handler)

    # Configure specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)

    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(f"logging configured - Level: {settings.LOG_LEVEL}, Environment: {settings.ENVIRONMENT}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module"""
    return logging.getLogger(name)
