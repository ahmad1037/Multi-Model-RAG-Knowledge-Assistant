import uuid

from fastapi.testclient import (
    TestClient,
)

from app.main import app


client = TestClient(app)


def test_upload_and_chunk_document():

    unique = uuid.uuid4().hex[:10]

    kb_response = client.post(
        "/api/v1/knowledge-bases",
        json={
            "name":
                f"Chunking Test {unique}",

            "slug":
                f"chunking-test-{unique}",

            "description":
                "Chunking integration test.",
        },
    )

    assert (
        kb_response.status_code
        == 201
    )

    kb_id = (
        kb_response.json()["id"]
    )

    text = """
PROJECT RESULTS

Gradient Boosting achieved the
best final performance.

MODEL COMPARISON

The tuned XGBoost model was also
evaluated but produced higher RMSE.

DEPLOYMENT

The final model was served using
FastAPI and Docker.
"""

    upload_response = client.post(
        (
            f"/api/v1/knowledge-bases/"
            f"{kb_id}/documents"
        ),
        files={
            "file": (
                "report.md",
                text.encode("utf-8"),
                "text/markdown",
            )
        },
    )

    assert (
        upload_response.status_code
        == 201
    )

    document_id = (
        upload_response.json()
        ["document"]["id"]
    )

    chunk_response = client.post(
        (
            f"/api/v1/documents/"
            f"{document_id}/chunk"
        ),
        json={
            "strategy":
                "structure_recursive_v1",

            "chunk_size_tokens":
                120,

            "chunk_overlap_tokens":
                20,

            "tokenizer_name":
                "cl100k_base",
        },
    )

    assert (
        chunk_response.status_code
        == 200
    )

    body = chunk_response.json()

    assert (
        body["run"]["status"]
        == "succeeded"
    )

    assert (
        body["run"]["chunk_count"]
        > 0
    )

    assert (
        body["preview"]
    )