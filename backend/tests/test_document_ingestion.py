import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import documents
from app.db.session import get_db


def test_upload_text_document_queues_processing(monkeypatch):
    app = FastAPI()
    app.include_router(documents.router, prefix="/api/v1")
    db = Mock()
    app.dependency_overrides[get_db] = lambda: db
    kb_id, document_id, job_id = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    now = datetime.now(timezone.utc)
    document = SimpleNamespace(
        id=document_id,
        knowledge_base_id=kb_id,
        original_filename="notes.txt",
        media_type="text/plain",
        file_size_bytes=12,
        page_count=None,
        status="uploaded",
        error_message=None,
        created_at=now,
        updated_at=now,
    )

    async def prepare_document_upload(*, db, knowledge_base_id, upload):
        assert knowledge_base_id == kb_id
        assert upload.filename == "notes.txt"
        return document

    enqueue = Mock(return_value=SimpleNamespace(
        id=job_id,
        document_id=document_id,
        job_type="document_processing",
        status="queued",
        current_stage="queued",
        progress_percent=0,
        celery_task_id="task-id",
        attempt_count=0,
        error_message=None,
        started_at=None,
        finished_at=None,
        created_at=now,
        updated_at=now,
    ))
    monkeypatch.setattr(documents, "prepare_document_upload", prepare_document_upload)
    monkeypatch.setattr(documents, "enqueue_document_processing", enqueue)

    response = TestClient(app).post(
        f"/api/v1/knowledge-bases/{kb_id}/documents",
        files={"file": ("notes.txt", b"Model result", "text/plain")},
    )

    assert response.status_code == 202
    assert response.json()["document"]["id"] == str(document_id)
    assert response.json()["processing_job"]["status"] == "queued"
    enqueue.assert_called_once_with(db=db, document_id=document_id)
