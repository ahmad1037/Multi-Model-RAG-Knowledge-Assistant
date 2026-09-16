import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import documents
from app.db.session import get_db


def test_chunk_document_returns_run_and_preview(monkeypatch):
    app = FastAPI()
    app.include_router(documents.router, prefix="/api/v1")
    db = Mock()
    app.dependency_overrides[get_db] = lambda: db
    document_id, run_id = uuid.uuid4(), uuid.uuid4()
    run = SimpleNamespace(
        id=run_id,
        document_id=document_id,
        strategy="structure_recursive_v1",
        tokenizer_name="cl100k_base",
        chunk_size_tokens=120,
        chunk_overlap_tokens=20,
        status="succeeded",
        is_active=True,
        chunk_count=1,
        average_tokens=8.0,
        max_tokens=8,
        error_message=None,
        created_at=datetime.now(timezone.utc),
    )
    chunk = SimpleNamespace(
        id=uuid.uuid4(),
        chunking_run_id=run_id,
        chunk_index=0,
        text="Gradient Boosting achieved the best final performance.",
        heading="PROJECT RESULTS",
        page_start=1,
        page_end=1,
        token_count=8,
    )
    run_chunking = Mock(return_value=(run, [chunk]))
    monkeypatch.setattr(documents, "run_chunking", run_chunking)

    response = TestClient(app).post(
        f"/api/v1/documents/{document_id}/chunk",
        json={
            "strategy": "structure_recursive_v1",
            "chunk_size_tokens": 120,
            "chunk_overlap_tokens": 20,
            "tokenizer_name": "cl100k_base",
        },
    )

    assert response.status_code == 200
    assert response.json()["run"]["chunk_count"] == 1
    assert response.json()["preview"][0]["text"] == chunk.text
    assert run_chunking.call_args.kwargs["db"] is db
    assert run_chunking.call_args.kwargs["document_id"] == document_id
