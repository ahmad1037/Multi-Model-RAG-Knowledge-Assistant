from functools import lru_cache

import numpy as np

from sentence_transformers import (
    SentenceTransformer,
)

from app.core.config import settings

import torch

class EmbeddingInputTooLongError(
    ValueError
):
    pass


class TextEmbedder:

    def __init__(self):

        self.model_name = (
            settings.text_embedding_model
        )

        self.dimension = (
            settings.text_embedding_dimension
        )

        self.batch_size = (
            settings.text_embedding_batch_size
        )

        self.query_instruction = (
            settings.text_query_instruction
        )

        self.device = settings.text_embedding_device.lower()

        if self.device == "cuda" and not torch.cuda.is_available():
            raise RuntimeError(
                "TEXT_EMBEDDING_DEVICE=cuda, but CUDA is unavailable in this runtime."
            )

        self.model = SentenceTransformer(
            settings.text_embedding_model,
            device=self.device,
        )

        self.tokenizer = (
            self.model.tokenizer
        )

        self.max_sequence_length = (
            self.model.max_seq_length
        )

        actual_dimension = (
            self.model
            .get_sentence_embedding_dimension()
        )

        if (
            actual_dimension
            != self.dimension
        ):

            raise RuntimeError(
                "Embedding dimension mismatch: "
                f"configuration={self.dimension}, "
                f"model={actual_dimension}"
            )

    def token_length(
        self,
        text: str,
    ) -> int:

        encoded = self.tokenizer(
            text,
            add_special_tokens=True,
            truncation=False,
        )

        return len(
            encoded["input_ids"]
        )

    def validate_text(
        self,
        text: str,
    ) -> None:

        length = self.token_length(
            text
        )

        if (
            length
            > self.max_sequence_length
        ):

            raise EmbeddingInputTooLongError(
                f"Text requires {length} model "
                f"tokens but {self.model_name} "
                f"supports a maximum of "
                f"{self.max_sequence_length}."
            )

    def encode_passages(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        for text in texts:
            self.validate_text(
                text
            )

        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

        embeddings = np.asarray(
            embeddings,
            dtype=np.float32,
        )

        return embeddings.tolist()

    def encode_query(
        self,
        query: str,
    ) -> list[float]:

        query_text = (
            self.query_instruction
            + query.strip()
        )

        self.validate_text(
            query_text
        )

        embedding = self.model.encode(
            query_text,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

        return (
            np.asarray(
                embedding,
                dtype=np.float32,
            )
            .tolist()
        )


@lru_cache
def get_text_embedder() -> TextEmbedder:

    return TextEmbedder()