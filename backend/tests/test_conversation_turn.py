import json
import uuid
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.schemas import conversation_turn


def test_answer_sources_with_uuids_can_be_saved(monkeypatch):
    conversation = SimpleNamespace(id=uuid.uuid4(), knowledge_base_id=uuid.uuid4(), summary=None, title="Test")
    document_id, visual_id = uuid.uuid4(), uuid.uuid4()
    saved = []
    db = Mock()
    db.add.side_effect = saved.append

    def commit():
        for message in saved:
            json.dumps(message.message_metadata)
            json.dumps(message.citations)
            if message.id is None:
                message.id = uuid.uuid4()

    db.commit.side_effect = commit
    monkeypatch.setattr(conversation_turn, "get_conversation", Mock(return_value=conversation))
    monkeypatch.setattr(conversation_turn, "recent_messages", Mock(return_value=[]))
    monkeypatch.setattr(conversation_turn, "rewrite_question", Mock(return_value=SimpleNamespace(
        standalone_question="What is shown?", depends_on_history=False,
        resolved_references=[], clarification_needed=False,
    )))
    monkeypatch.setattr(conversation_turn, "answer_question", Mock(return_value={
        "answer": "A chart [S1]", "citations": ["S1"], "answerable": True,
        "grounding_verified": True,
        "sources": [{"source_id": "S1", "document_id": document_id, "visual_asset_id": visual_id}],
    }))
    monkeypatch.setattr(conversation_turn, "maybe_update_summary", Mock())

    result = conversation_turn.run_conversation_turn(db, conversation.id, "What is shown?")

    assert result["answer"] == "A chart [S1]"
    assert len(saved) == 2
    assert saved[1].message_metadata["sources"][0]["document_id"] == str(document_id)
    assert saved[1].message_metadata["sources"][0]["visual_asset_id"] == str(visual_id)


def test_greeting_after_document_answer_bypasses_rag(monkeypatch):
    conversation = SimpleNamespace(
        id=uuid.uuid4(), knowledge_base_id=uuid.uuid4(),
        summary="Gradient Boosting was selected over XGBoost.", title="Models",
    )
    saved = []
    db = Mock()
    db.add.side_effect = saved.append
    db.commit.side_effect = lambda: [setattr(m, "id", uuid.uuid4()) for m in saved if m.id is None]
    monkeypatch.setattr(conversation_turn, "get_conversation", Mock(return_value=conversation))
    monkeypatch.setattr(conversation_turn, "recent_messages", Mock(return_value=[
        SimpleNamespace(role="user", content="Why Gradient Boosting instead of XGBoost?"),
        SimpleNamespace(role="assistant", content="It had the lowest MAE. [S1]"),
    ]))
    rewrite = Mock(side_effect=AssertionError("Social turns must not be rewritten"))
    answer = Mock(side_effect=AssertionError("Social turns must not retrieve evidence"))
    summary = Mock()
    monkeypatch.setattr(conversation_turn, "rewrite_question", rewrite)
    monkeypatch.setattr(conversation_turn, "answer_question", answer)
    monkeypatch.setattr(conversation_turn, "maybe_update_summary", summary)

    result = conversation_turn.run_conversation_turn(db, conversation.id, "Hi!")

    assert result["answer"] == "Hi! How can I help you with your documents?"
    assert result["citations"] == result["sources"] == []
    assert result["depends_on_history"] is False
    assert result["grounding_verified"] is False
    assert len(saved) == 2
    assert saved[1].content == result["answer"]
    assert saved[1].message_metadata["sources"] == []
    summary.assert_not_called()


def test_social_routing_preserves_questions_and_followups():
    from app.rag.memory.social import social_reply

    for message in ["Hi, why Gradient Boosting?", "Thanks, what about XGBoost?",
                    "How much better?", "What does HI mean?", "hello.py", "yes"]:
        assert social_reply(message) is None
    for message in ["Hi", " HELLO! ", "Hey there", "Good morning", "Thank you!", "Bye"]:
        assert social_reply(message) is not None


def test_model_connection_failure_does_not_save_user_message(monkeypatch):
    conversation = SimpleNamespace(id=uuid.uuid4(), summary=None)
    db = Mock()
    monkeypatch.setattr(conversation_turn, "get_conversation", Mock(return_value=conversation))
    monkeypatch.setattr(conversation_turn, "recent_messages", Mock(return_value=[]))
    monkeypatch.setattr(
        conversation_turn,
        "rewrite_question",
        Mock(side_effect=ConnectionError("Ollama unavailable")),
    )

    with pytest.raises(ConnectionError):
        conversation_turn.run_conversation_turn(db, conversation.id, "What does the chart show?")

    db.add.assert_not_called()
    db.commit.assert_not_called()
