import uuid

from time import perf_counter

import structlog

from fastapi import Request

from app.observability.context import (
    request_id_var,
)

from app.observability.logging import (
    get_logger,
)

from app.observability.metrics import (
    HTTP_LATENCY,
    HTTP_REQUESTS,
    IN_FLIGHT_REQUESTS,
)


logger = get_logger()


async def observability_middleware(
    request: Request,
    call_next,
):

    request_id = (
        request.headers.get(
            "X-Request-ID"
        )
        or str(uuid.uuid4())
    )

    token = request_id_var.set(
        request_id
    )

    structlog.contextvars.bind_contextvars(
        request_id=request_id
    )

    started = perf_counter()

    IN_FLIGHT_REQUESTS.inc()

    response = None

    try:

        response = await call_next(
            request
        )

        response.headers[
            "X-Request-ID"
        ] = request_id

        return response

    finally:

        duration = (
            perf_counter()
            - started
        )

        route = request.scope.get(
            "route"
        )

        route_name = (
            getattr(
                route,
                "path",
                None,
            )
            or request.url.path
        )

        status_code = (
            response.status_code
            if response is not None
            else 500
        )

        status_class = (
            f"{status_code // 100}xx"
        )

        HTTP_REQUESTS.labels(
            method=request.method,
            route=route_name,
            status_class=status_class,
        ).inc()

        HTTP_LATENCY.labels(
            method=request.method,
            route=route_name,
        ).observe(
            duration
        )

        IN_FLIGHT_REQUESTS.dec()

        logger.info(
            "http_request_complete",

            method=request.method,

            route=route_name,

            status_code=status_code,

            duration_ms=round(
                duration * 1000,
                2,
            ),
        )

        structlog.contextvars.clear_contextvars()

        request_id_var.reset(
            token
        )