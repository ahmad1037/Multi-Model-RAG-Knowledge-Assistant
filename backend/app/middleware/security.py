from fastapi import Request

from app.core.config import settings


async def security_headers_middleware(
    request: Request,
    call_next,
):

    response = await call_next(
        request
    )


    if not (
        settings
        .security_headers_enabled
    ):

        return response


    response.headers[
        "X-Content-Type-Options"
    ] = "nosniff"


    response.headers[
        "X-Frame-Options"
    ] = "DENY"


    response.headers[
        "Referrer-Policy"
    ] = (
        "strict-origin-when-cross-origin"
    )


    response.headers[
        "Permissions-Policy"
    ] = (
        "camera=(), "
        "microphone=(), "
        "geolocation=()"
    )


    if (
        request.url.scheme
        == "https"
    ):

        response.headers[
            "Strict-Transport-Security"
        ] = (
            "max-age=31536000; "
            "includeSubDomains"
        )


    return response