import uuid
from unittest.mock import Mock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import conversations
from app.db.session import get_db


def test_message_endpoint_returns_503_when_ollama_is_unavailable(monkeypatch):
    app = FastAPI()
    app.include_router(conversations.router, prefix="/api/v1")
    app.dependency_overrides[get_db] = lambda: Mock()
    monkeypatch.setattr(
        conversations,
        "run_conversation_turn",
        Mock(side_effect=ConnectionError("Failed to connect to Ollama")),
    )

    response = TestClient(app).post(
        f"/api/v1/conversations/{uuid.uuid4()}/messages",
        json={"message": "What does the chart show?"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "The language model service is unavailable. Please try again shortly."
    )
