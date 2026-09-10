from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.core.config import settings
from app.api.routes.knowledge_bases import (
    router as knowledge_bases_router,
)
from app.api.routes.documents import (
    router as documents_router,
)
from app.api.routes.retrieval import (
    router as retrieval_router,
)
from app.api.routes.visual_retrieval import (
    router as visual_retrieval_router,
)
from app.api.routes.visual_assets import (
    router as visual_assets_router,
)
from app.api.routes.generation import (
    router as generation_router,
)
from app.api.routes import (
    conversations,
)
from prometheus_client import (
    make_asgi_app,
)
from app.middleware.observability import (
    observability_middleware,
)
from app.observability.logging import (
    configure_logging,
)

configure_logging()
app = FastAPI(
    title="Multimodal RAG Knowledge Assistant API",
    description=(
        "Backend API for document ingestion, multimodal retrieval, "
        "RAG generation, conversations, and evaluation."
    ),
    version="0.1.0",
)

app.middleware("http")(
    observability_middleware
)

metrics_app = make_asgi_app()

app.mount(
    "/metrics",
    metrics_app,
)

app.include_router(
    knowledge_bases_router,
    prefix="/api/v1",
)

app.include_router(
    documents_router,
    prefix="/api/v1",
)

app.include_router(
    retrieval_router,
    prefix="/api/v1",
)

app.include_router(
    visual_retrieval_router,
    prefix="/api/v1",
)
app.include_router(
    visual_assets_router,
    prefix="/api/v1",
)

app.include_router(
    generation_router,
    prefix="/api/v1",
)

app.include_router(
    conversations.router,
    prefix="/api/v1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
        "X-Request-ID",
    ],
)

app.middleware("http")(
    observability_middleware
)

metrics_app = make_asgi_app()

app.mount(
    "/metrics",
    metrics_app,
)

app.include_router(
    health_router,
    prefix="/api/v1",
)




@app.get("/")
def root():
    return {
        "name": "Multimodal RAG Knowledge Assistant",
        "version": "0.1.0",
    }