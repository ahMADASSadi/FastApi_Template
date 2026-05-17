import logging
from typing import Any

from rich.console import Console
from rich.logging import RichHandler


def get_logging_config(
    env: str = "development",
    log_level: str = "INFO",
) -> dict[str, Any]:
    """Generate logging configuration for FastAPI/Uvicorn/Gunicorn."""

    is_development = env.lower() == "development"

    # Console handler with Rich (pretty output in dev)
    console_handler = RichHandler(
        console=Console(stderr=True),
        show_time=True,
        show_path=is_development,
        markup=True,
        rich_tracebacks=True,
        tracebacks_show_locals=is_development,
    )
    console_handler.setLevel(getattr(logging, log_level.upper()))

    # # JSON handler for production (for log aggregation)
    # json_handler = logging.StreamHandler(sys.stdout)
    # json_handler.setFormatter(
    #     jsonlogger.JsonFormatter(
    #         fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
    #         rename_fields={
    #             "levelname": "level",
    #             "asctime": "timestamp",
    #             "name": "logger",
    #         },
    #         datefmt="%Y-%m-%d %H:%M:%S",
    #     )
    # )

    # Choose handlers based on environment
    handlers = [console_handler]  # if is_development else [json_handler]

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": (
                    "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s"
                ),
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": console_handler,
            # "json": json_handler,
        },
        "root": {
            "level": log_level.upper(),
            "handlers": handlers,
        },
        "loggers": {
            "uvicorn": {
                "level": log_level.upper(),
                "handlers": handlers,
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "WARNING" if is_development else "INFO",
                "handlers": handlers,
                "propagate": False,
            },
            "uvicorn.error": {
                "level": "INFO",
                "handlers": handlers,
                "propagate": False,
            },
            "gunicorn": {
                "level": log_level.upper(),
                "handlers": handlers,
                "propagate": False,
            },
            "gunicorn.access": {
                "level": "WARNING" if is_development else "INFO",
                "handlers": handlers,
                "propagate": False,
            },
            "gunicorn.error": {
                "level": "INFO",
                "handlers": handlers,
                "propagate": False,
            },
            "fastapi": {
                "level": log_level.upper(),
                "handlers": handlers,
                "propagate": False,
            },
            "sqlalchemy": {
                "level": "WARNING" if is_development else "ERROR",
                "handlers": handlers,
                "propagate": False,
            },
            "alembic": {
                "level": "INFO",
                "handlers": handlers,
                "propagate": False,
            },
        },
    }
