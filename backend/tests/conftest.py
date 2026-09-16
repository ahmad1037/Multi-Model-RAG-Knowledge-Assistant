import socket
from ipaddress import ip_address

import pytest


@pytest.fixture(autouse=True)
def block_network_and_model_inference(monkeypatch):
    """Normal tests must use mocks for external services and model inference."""

    def blocked(*_args, **_kwargs):
        raise AssertionError("Network access and model inference must be mocked in tests.")

    original_connect = socket.socket.connect
    original_create_connection = socket.create_connection

    def is_loopback(address):
        if not isinstance(address, tuple):
            return True  # Unix-domain sockets used by the test harness.
        host = address[0]
        if host == "localhost":
            return True
        try:
            return ip_address(host).is_loopback
        except ValueError:
            return False

    def guarded_connect(sock, address):
        if not is_loopback(address):
            blocked()
        return original_connect(sock, address)

    def guarded_create_connection(address, *args, **kwargs):
        if not is_loopback(address):
            blocked()
        return original_create_connection(address, *args, **kwargs)

    monkeypatch.setattr(socket.socket, "connect", guarded_connect)
    monkeypatch.setattr(socket, "create_connection", guarded_create_connection)

    from app.rag.embeddings.text_embedder import TextEmbedder
    from app.rag.generation.ollama_provider import OllamaGenerationProvider
    from app.rag.reranking.bge_reranker import BGEReranker
    from app.rag.vision.clip_embedder import CLIPEmbedder
    from app.rag.vision.vlm import QwenVisualAnalyzer

    for model_class in (
        TextEmbedder,
        CLIPEmbedder,
        BGEReranker,
        QwenVisualAnalyzer,
        OllamaGenerationProvider,
    ):
        monkeypatch.setattr(model_class, "__init__", blocked)
