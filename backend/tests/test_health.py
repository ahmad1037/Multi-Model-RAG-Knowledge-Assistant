from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_liveness():
    response = client.get(
        "/api/v1/health/live"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "ok"