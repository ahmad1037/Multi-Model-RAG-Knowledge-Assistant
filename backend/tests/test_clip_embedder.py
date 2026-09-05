import torch

from app.rag.vision.clip_embedder import (
    CLIPEmbedder,
)


def test_clip_normalization():

    values = torch.tensor(
        [
            [3.0, 4.0],
            [5.0, 12.0],
        ]
    )

    normalized = (
        CLIPEmbedder._normalize(
            values
        )
    )

    norms = normalized.norm(
        dim=-1
    )

    assert torch.allclose(
        norms,
        torch.ones_like(norms),
        atol=1e-6,
    )