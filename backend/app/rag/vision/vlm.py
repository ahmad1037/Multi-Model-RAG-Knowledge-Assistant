from functools import lru_cache
from pathlib import Path

import torch

from PIL import Image

from transformers import (
    AutoProcessor,
    Qwen2_5_VLForConditionalGeneration,
)

from app.core.config import settings


class QwenVisualAnalyzer:

    def __init__(self):

        self.model_name = (
            settings.vlm_model
        )

        self.processor = (
            AutoProcessor.from_pretrained(
                self.model_name,

                min_pixels=(
                    settings.vlm_min_pixels
                ),

                max_pixels=(
                    settings.vlm_max_pixels
                ),
            )
        )

        self.model = (
            Qwen2_5_VLForConditionalGeneration
            .from_pretrained(
                self.model_name,
                torch_dtype="auto",
                device_map="auto",
            )
        )

        self.model.eval()


    def analyze(
        self,
        image_path: Path,
        prompt: str,
    ) -> str:

        with Image.open(
            image_path
        ) as image:

            image = image.convert(
                "RGB"
            )

            conversation = [
                {
                    "role": "user",

                    "content": [
                        {
                            "type": "image"
                        },

                        {
                            "type": "text",
                            "text": prompt,
                        },
                    ],
                }
            ]

            formatted_prompt = (
                self.processor
                .apply_chat_template(
                    conversation,
                    tokenize=False,
                    add_generation_prompt=True,
                )
            )

            inputs = self.processor(
                text=[
                    formatted_prompt
                ],

                images=[
                    image
                ],

                padding=True,

                return_tensors="pt",
            )

        inputs = inputs.to(
            self.model.device
        )

        with torch.inference_mode():

            generated_ids = (
                self.model.generate(
                    **inputs,

                    max_new_tokens=(
                        settings
                        .vlm_max_new_tokens
                    ),

                    do_sample=False,
                )
            )

        generated_only = [
            output[
                len(input_ids):
            ]

            for input_ids, output
            in zip(
                inputs.input_ids,
                generated_ids,
                strict=True,
            )
        ]

        text = (
            self.processor
            .batch_decode(
                generated_only,

                skip_special_tokens=True,

                clean_up_tokenization_spaces=False,
            )[0]
        )

        return text.strip()


@lru_cache
def get_visual_analyzer():

    return QwenVisualAnalyzer()