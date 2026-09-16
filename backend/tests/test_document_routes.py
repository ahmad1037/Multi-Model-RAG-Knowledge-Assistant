import uuid
from datetime import datetime, timezone
from unittest.mock import Mock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import documents, processing_jobs
from app.db.session import get_db


def test_document_list_get_needs_only_knowledge_base_path(monkeypatch):
    app = FastAPI()
    app.include_router(documents.router, prefix="/api/v1")
    session = object()
    app.dependency_overrides[get_db] = lambda: session
    knowledge_base_id = uuid.uuid4()
    calls = []

    def fake_list(db, kb_id):
        calls.append((db, kb_id))
        return []

    monkeypatch.setattr(documents, "list_documents", fake_list)
    response = TestClient(app).get(
        f"/api/v1/knowledge-bases/{knowledge_base_id}/documents"
    )

    assert response.status_code == 200
    assert response.json() == []
    assert calls == [(session, knowledge_base_id)]


def test_processing_contract_has_path_id_and_no_required_body():
    app = FastAPI()
    app.include_router(processing_jobs.router)
    operation = app.openapi()["paths"]["/documents/{document_id}/process-async"]["post"]

    assert "requestBody" not in operation
    assert [(p["name"], p["in"]) for p in operation["parameters"]] == [
        ("document_id", "path")
    ]


def test_processing_missing_document_returns_404_without_enqueue(monkeypatch):
    app = FastAPI()
    app.include_router(processing_jobs.router, prefix="/api/v1")
    session = object()
    app.dependency_overrides[get_db] = lambda: session
    document_id = uuid.uuid4()
    lookup = Mock(return_value=None)
    enqueue = Mock()
    monkeypatch.setattr(processing_jobs, "get_document", lookup)
    monkeypatch.setattr(processing_jobs, "enqueue_document_processing", enqueue)

    response = TestClient(app).post(f"/api/v1/documents/{document_id}/process-async")

    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found."}
    lookup.assert_called_once_with(session, document_id)
    enqueue.assert_not_called()


def test_processing_existing_document_returns_accepted_job(monkeypatch):
    app = FastAPI()
    app.include_router(processing_jobs.router, prefix="/api/v1")
    session = object()
    app.dependency_overrides[get_db] = lambda: session
    document_id = uuid.uuid4()
    job_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    enqueue = Mock(return_value={
        "id": job_id,
        "document_id": document_id,
        "job_type": "document_processing",
        "status": "queued",
        "current_stage": "queued",
        "progress_percent": 0,
        "celery_task_id": "task-id",
        "attempt_count": 0,
        "error_message": None,
        "started_at": None,
        "finished_at": None,
        "created_at": now,
        "updated_at": now,
    })
    monkeypatch.setattr(processing_jobs, "get_document", Mock(return_value=object()))
    monkeypatch.setattr(processing_jobs, "enqueue_document_processing", enqueue)

    response = TestClient(app).post(f"/api/v1/documents/{document_id}/process-async")

    assert response.status_code == 202
    assert response.json()["id"] == str(job_id)
    enqueue.assert_called_once_with(session, document_id)
