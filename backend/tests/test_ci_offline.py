import socket

import pytest

from app.rag.embeddings.text_embedder import TextEmbedder
from app.rag.generation.ollama_provider import OllamaGenerationProvider
from app.rag.reranking.bge_reranker import BGEReranker
from app.rag.vision.clip_embedder import CLIPEmbedder
from app.rag.vision.vlm import QwenVisualAnalyzer


@pytest.mark.parametrize(
    "model_class",
    [TextEmbedder, CLIPEmbedder, BGEReranker, QwenVisualAnalyzer, OllamaGenerationProvider],
)
def test_model_initialization_is_blocked_in_normal_tests(model_class):
    with pytest.raises(AssertionError, match="must be mocked"):
        model_class()


def test_external_network_is_blocked_in_normal_tests():
    with pytest.raises(AssertionError, match="must be mocked"):
        socket.create_connection(("example.com", 443), timeout=0.1)
