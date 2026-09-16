import uuid
from unittest.mock import Mock

from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api.routes.knowledge_bases import router
from app.db.session import get_db


def test_delete_knowledge_base_returns_empty_204():
    app = FastAPI()
    app.include_router(router)
    db = Mock()
    kb_id = uuid.uuid4()
    db.scalar.return_value = kb_id
    app.dependency_overrides[get_db] = lambda: db
    response = TestClient(app).delete(f"/knowledge-bases/{kb_id}")
    assert response.status_code == 204
    assert response.content == b""
    db.commit.assert_called_once()


def test_delete_missing_knowledge_base_returns_404():
    app = FastAPI()
    app.include_router(router)
    db = Mock()
    db.scalar.return_value = None
    app.dependency_overrides[get_db] = lambda: db
    response = TestClient(app).delete(f"/knowledge-bases/{uuid.uuid4()}")
    assert response.status_code == 404
    db.commit.assert_not_called()
