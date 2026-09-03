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

app = FastAPI(
    title="Multimodal RAG Knowledge Assistant API",
    description=(
        "Backend API for document ingestion, multimodal retrieval, "
        "RAG generation, conversations, and evaluation."
    ),
    version="0.1.0",
)

app.include_router(
    documents_router,
    prefix="/api/v1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    health_router,
    prefix="/api/v1",
)

app.include_router(
    knowledge_bases_router,
    prefix="/api/v1",
)


@app.get("/")
def root():
    return {
        "name": "Multimodal RAG Knowledge Assistant",
        "version": "0.1.0",
    }