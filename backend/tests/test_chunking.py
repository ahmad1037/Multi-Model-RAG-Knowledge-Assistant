from app.rag.chunking.strategies import (
    chunk_pages,
)
from app.rag.chunking.types import (
    ChunkingConfig,
)


def test_structure_chunking():

    pages = [
        {
            "page_number": 1,
            "text": """
MODEL EVALUATION

Gradient Boosting achieved the best
test RMSE.

It outperformed the tuned XGBoost
model on the held-out future period.

DEPLOYMENT

The final model was deployed using
FastAPI and Docker.
""",
        }
    ]

    config = ChunkingConfig(
        strategy=(
            "structure_recursive_v1"
        ),
        chunk_size_tokens=100,
        chunk_overlap_tokens=20,
        tokenizer_name="cl100k_base",
    )

    chunks = chunk_pages(
        pages,
        config,
    )

    assert len(chunks) > 0

    assert all(
        chunk.text.strip()
        for chunk in chunks
    )

    assert all(
        chunk.token_count
        <= config.chunk_size_tokens
        for chunk in chunks
    )

    assert any(
        chunk.heading
        == "MODEL EVALUATION"
        for chunk in chunks
    )