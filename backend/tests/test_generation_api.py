import uuid
from unittest.mock import Mock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import generation
from app.db.session import get_db
from app.models.knowledge_base import KnowledgeBase
from app.services import grounded_generation
from app.services.hybrid_retrieval import NoHybridResultsError


def test_unknown_knowledge_base_returns_404_without_retrieval(monkeypatch):
    app = FastAPI()
    app.include_router(generation.router, prefix="/api/v1")
    db = Mock()
    db.get.return_value = None
    app.dependency_overrides[get_db] = lambda: db
    answer = Mock()
    monkeypatch.setattr(generation, "answer_question", answer)
    kb_id = uuid.uuid4()

    response = TestClient(app).post(
        f"/api/v1/knowledge-bases/{kb_id}/answer", json={"question": "What are the findings?"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Knowledge base not found."}
    db.get.assert_called_once_with(KnowledgeBase, kb_id)
    answer.assert_not_called()


def test_no_evidence_returns_normal_refusal_without_model_call(monkeypatch):
    app = FastAPI()
    app.include_router(generation.router, prefix="/api/v1")
    db = Mock()
    db.get.return_value = object()
    app.dependency_overrides[get_db] = lambda: db
    monkeypatch.setattr(grounded_generation, "retrieve_rerank_and_select", Mock(
        side_effect=NoHybridResultsError("No retrieval channel returned evidence."),
    ))
    provider = Mock()
    monkeypatch.setattr(grounded_generation, "get_generation_provider", provider)

    response = TestClient(app).post(
        f"/api/v1/knowledge-bases/{uuid.uuid4()}/answer", json={"question": "What are the findings?"},
    )

    assert response.status_code == 200
    assert response.json()["answerable"] is False
    assert response.json()["sources"] == []
    assert response.json()["citations"] == []
    provider.assert_not_called()


def test_empty_refusal_returns_explanation(monkeypatch):
    from app.schemas.generation import GroundedModelOutput

    monkeypatch.setattr(grounded_generation, "retrieve_rerank_and_select", Mock(
        return_value={"context": {"items": [{"citation_id": "S1"}]}},
    ))
    monkeypatch.setattr(grounded_generation, "format_context", Mock(return_value="Evidence"))
    generate = Mock()
    monkeypatch.setattr(grounded_generation, "generate_with_valid_citations", generate)
    for reason in ["The evidence does not explain the final model selection.", "", "   "]:
        generate.return_value = (GroundedModelOutput(
            answerable=False, answer=" \n ", citations=[], refusal_reason=reason,
        ), [])
        result = grounded_generation.answer_question(Mock(), uuid.uuid4(), "Why this model?")
        assert result["answer"].strip()
        if reason.strip():
            assert result["answer"] == reason
        assert result["answerable"] is False
        assert result["citations"] == result["sources"] == []
