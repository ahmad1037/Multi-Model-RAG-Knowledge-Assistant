from functools import lru_cache

import numpy as np
import torch

from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
)

from app.core.config import settings
from app.core.device import resolve_device


class BGEReranker:

    def __init__(self):

        self.model_name = (
            settings.reranker_model
        )

        self.batch_size = (
            settings.reranker_batch_size
        )

        self.max_length = (
            settings.reranker_max_length
        )

        self.device = resolve_device(
            settings.reranker_device
        )

        self.tokenizer = (
            AutoTokenizer
            .from_pretrained(
                self.model_name
            )
        )

        self.model = (
            AutoModelForSequenceClassification
            .from_pretrained(
                self.model_name
            )
        )

        self.model = self.model.to(
            self.device
        )

        self.model.eval()

    def score_pairs(
        self,
        query: str,
        passages: list[str],
    ) -> list[float]:

        if not passages:
            return []

        scores: list[float] = []

        for start in range(
            0,
            len(passages),
            self.batch_size,
        ):

            batch_passages = passages[
                start:
                start + self.batch_size
            ]

            pairs = [
                [
                    query,
                    passage,
                ]
                for passage
                in batch_passages
            ]

            encoded = self.tokenizer(
                pairs,
                padding=True,
                truncation=True,
                max_length=self.max_length,
                return_tensors="pt",
            )

            encoded = {
                key: value.to(
                    self.device
                )
                for key, value
                in encoded.items()
            }

            with torch.inference_mode():

                logits = self.model(
                    **encoded,
                    return_dict=True,
                ).logits

            batch_scores = (
                logits
                .view(-1)
                .float()
                .cpu()
                .numpy()
                .astype(
                    np.float32
                )
                .tolist()
            )

            scores.extend(
                batch_scores
            )

        return scores


@lru_cache
def get_reranker() -> BGEReranker:

    return BGEReranker()