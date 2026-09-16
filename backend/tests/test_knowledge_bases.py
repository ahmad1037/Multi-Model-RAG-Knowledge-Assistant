import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import knowledge_bases
from app.db.session import get_db


def test_create_and_list_knowledge_base(monkeypatch):
    app = FastAPI()
    app.include_router(knowledge_bases.router, prefix="/api/v1")
    db = Mock()
    app.dependency_overrides[get_db] = lambda: db
    kb_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    created = SimpleNamespace(
        id=kb_id,
        name="Test Knowledge Base",
        slug="test-kb",
        description="Test knowledge base.",
        created_at=now,
        updated_at=now,
    )
    monkeypatch.setattr(knowledge_bases, "get_knowledge_base_by_slug", Mock(return_value=None))
    create = Mock(return_value=created)
    monkeypatch.setattr(knowledge_bases, "create_knowledge_base", create)
    monkeypatch.setattr(knowledge_bases, "list_knowledge_bases", Mock(return_value=[created]))
    client = TestClient(app)

    response = client.post(
        "/api/v1/knowledge-bases",
        json={"name": created.name, "slug": created.slug, "description": created.description},
    )

    assert response.status_code == 201
    assert response.json()["id"] == str(kb_id)
    create.assert_called_once()
    assert create.call_args.args[0] is db

    response = client.get("/api/v1/knowledge-bases")

    assert response.status_code == 200
    assert [item["slug"] for item in response.json()] == ["test-kb"]
