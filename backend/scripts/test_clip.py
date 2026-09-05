from pathlib import Path

from app.rag.vision.clip_embedder import (
    get_clip_embedder,
)


embedder = get_clip_embedder()


print(
    "Device:",
    embedder.device,
)

print(
    "Dimension:",
    embedder.dimension,
)


query_vector = (
    embedder.encode_text(
        "a bar chart comparing models"
    )
)

print(
    "Text vector length:",
    len(query_vector),
)


image_path = Path(
    "../storage/page_images/"
)

print(
    "CLIP initialized successfully."
)