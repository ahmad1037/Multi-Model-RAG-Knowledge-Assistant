import logging

import structlog

from app.core.config import settings


def configure_logging() -> None:

    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(message)s",
    )

    structlog.configure(
        processors=[
            structlog.contextvars
            .merge_contextvars,

            structlog.processors
            .add_log_level,

            structlog.processors
            .TimeStamper(
                fmt="iso",
                utc=True,
            ),

            structlog.processors
            .StackInfoRenderer(),

            structlog.processors
            .format_exc_info,

            structlog.processors
            .JSONRenderer(),
        ],

        logger_factory=(
            structlog.PrintLoggerFactory()
        ),

        cache_logger_on_first_use=True,
    )


def get_logger():
    return structlog.get_logger()