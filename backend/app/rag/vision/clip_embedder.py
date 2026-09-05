from functools import lru_cache
from pathlib import Path

import numpy as np
import open_clip
import torch

from PIL import Image

from app.core.config import settings
from app.rag.vision.device import (
    resolve_device,
)


class CLIPEmbedder:

    def __init__(self):

        self.model_name = (
            settings.clip_model_name
        )

        self.pretrained = (
            settings.clip_pretrained
        )

        self.dimension = (
            settings.clip_embedding_dimension
        )

        self.batch_size = (
            settings.clip_batch_size
        )

        self.device = resolve_device(
            settings.clip_device
        )

        (
            self.model,
            _,
            self.preprocess,
        ) = (
            open_clip
            .create_model_and_transforms(
                self.model_name,
                pretrained=self.pretrained,
            )
        )

        self.tokenizer = (
            open_clip.get_tokenizer(
                self.model_name
            )
        )

        self.model = self.model.to(
            self.device
        )

        self.model.eval()

        self._validate_dimension()

    def _validate_dimension(
        self,
    ) -> None:

        tokens = self.tokenizer(
            ["dimension check"]
        ).to(
            self.device
        )

        with torch.inference_mode():

            vector = (
                self.model
                .encode_text(tokens)
            )

        actual_dimension = (
            vector.shape[-1]
        )

        if (
            actual_dimension
            != self.dimension
        ):

            raise RuntimeError(
                "CLIP embedding dimension "
                "mismatch: "
                f"configured={self.dimension}, "
                f"actual={actual_dimension}"
            )

    @staticmethod
    def _normalize(
        tensor: torch.Tensor,
    ) -> torch.Tensor:

        return (
            tensor
            / tensor.norm(
                dim=-1,
                keepdim=True,
            ).clamp_min(
                1e-12
            )
        )

    def encode_texts(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        if not texts:
            return []

        vectors: list[
            list[float]
        ] = []

        for start in range(
            0,
            len(texts),
            self.batch_size,
        ):

            batch_texts = texts[
                start:
                start + self.batch_size
            ]

            tokens = self.tokenizer(
                batch_texts
            ).to(
                self.device
            )

            with torch.inference_mode():

                features = (
                    self.model
                    .encode_text(tokens)
                )

                features = (
                    self._normalize(
                        features
                    )
                )

            vectors.extend(
                features
                .float()
                .cpu()
                .numpy()
                .astype(
                    np.float32
                )
                .tolist()
            )

        return vectors

    def encode_text(
        self,
        text: str,
    ) -> list[float]:

        return self.encode_texts(
            [text]
        )[0]

    def encode_images(
        self,
        image_paths: list[Path],
    ) -> list[list[float]]:

        if not image_paths:
            return []

        vectors: list[
            list[float]
        ] = []

        for start in range(
            0,
            len(image_paths),
            self.batch_size,
        ):

            batch_paths = image_paths[
                start:
                start + self.batch_size
            ]

            tensors = []

            for path in batch_paths:

                with Image.open(
                    path
                ) as image:

                    image = (
                        image
                        .convert("RGB")
                    )

                    tensor = (
                        self.preprocess(
                            image
                        )
                    )

                    tensors.append(
                        tensor
                    )

            batch = torch.stack(
                tensors
            ).to(
                self.device
            )

            with torch.inference_mode():

                features = (
                    self.model
                    .encode_image(
                        batch
                    )
                )

                features = (
                    self._normalize(
                        features
                    )
                )

            vectors.extend(
                features
                .float()
                .cpu()
                .numpy()
                .astype(
                    np.float32
                )
                .tolist()
            )

        return vectors


@lru_cache
def get_clip_embedder() -> CLIPEmbedder:

    return CLIPEmbedder()