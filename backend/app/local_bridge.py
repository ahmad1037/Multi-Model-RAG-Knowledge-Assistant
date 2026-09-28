"""Authenticated entry point for a tunnel to this computer's RAG backend."""
import os
import secrets

from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.main import app as rag_app

token = os.environ.get("LOCAL_BRIDGE_TOKEN", "")
if len(token) < 32:
    raise RuntimeError("LOCAL_BRIDGE_TOKEN must contain at least 32 characters")


async def authenticated_app(scope, receive, send):
    if scope["type"] == "http":
        headers = dict(scope["headers"])
        supplied = headers.get(b"authorization", b"")
        if not secrets.compare_digest(supplied, f"Bearer {token}".encode()):
            await JSONResponse({"detail": "A valid local access key is required."}, status_code=401)(scope, receive, send)
            return
    await rag_app(scope, receive, send)


# CORS wraps authentication and the app so preflights and errors also work.
app = CORSMiddleware(
    authenticated_app,
    allow_origins=[os.environ["FRONTEND_ORIGIN"]],
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
    expose_headers=["X-Request-ID"],
)
