import uuid

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_upload_text_document():

    unique = uuid.uuid4().hex[:10]

    kb_response = client.post(
        "/api/v1/knowledge-bases",
        json={
            "name":
                f"Ingestion Test {unique}",

            "slug":
                f"ingestion-test-{unique}",

            "description":
                "Temporary ingestion test.",
        },
    )

    assert (
        kb_response.status_code
        == 201
    )

    knowledge_base_id = (
        kb_response.json()["id"]
    )

    response = client.post(
        (
            "/api/v1/knowledge-bases/"
            f"{knowledge_base_id}"
            "/documents"
        ),
        files={
            "file": (
                "notes.txt",
                (
                    b"Gradient Boosting achieved "
                    b"the best forecasting RMSE."
                ),
                "text/plain",
            )
        },
    )

    assert (
        response.status_code
        == 201
    )

    result = response.json()

    assert (
        result["document"]["status"]
        == "ready_for_chunking"
    )

    assert (
        result["text_characters"]
        > 0
    )

    assert (
        result["visual_assets"]
        == 0
    )