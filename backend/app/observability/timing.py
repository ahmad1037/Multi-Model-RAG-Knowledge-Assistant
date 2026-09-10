from contextlib import contextmanager
from time import perf_counter

from app.observability.logging import (
    get_logger,
)

from app.observability.metrics import (
    RAG_STAGE_ERRORS,
    RAG_STAGE_LATENCY,
)


logger = get_logger()


@contextmanager
def observe_stage(
    stage: str,
    **metadata,
):

    started = perf_counter()

    try:

        yield

    except Exception as exc:

        RAG_STAGE_ERRORS.labels(
            stage=stage,
            error_type=(
                type(exc).__name__
            ),
        ).inc()

        logger.exception(
            "rag_stage_failed",
            stage=stage,
            **metadata,
        )

        raise

    finally:

        duration = (
            perf_counter()
            - started
        )

        RAG_STAGE_LATENCY.labels(
            stage=stage
        ).observe(
            duration
        )

        logger.info(
            "rag_stage_complete",

            stage=stage,

            duration_ms=round(
                duration * 1000,
                2,
            ),

            **metadata,
        )