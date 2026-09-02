import uuid

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_and_list_knowledge_base():
    unique = uuid.uuid4().hex[:10]

    payload = {
        "name": f"Test Knowledge Base {unique}",
        "slug": f"test-kb-{unique}",
        "description": "Test knowledge base.",
    }

    create_response = client.post(
        "/api/v1/knowledge-bases",
        json=payload,
    )

    assert create_response.status_code == 201

    created = create_response.json()

    assert created["name"] == payload["name"]
    assert created["slug"] == payload["slug"]

    list_response = client.get(
        "/api/v1/knowledge-bases"
    )

    assert list_response.status_code == 200

    items = list_response.json()

    assert any(
        item["slug"] == payload["slug"]
        for item in items
    )