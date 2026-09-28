import hashlib
import uuid
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.services import document_ingestion as ingestion
from app.services.file_storage import StorageManager


@pytest.mark.parametrize("valid", [True, False])
def test_cloud_source_is_verified_before_parsing(tmp_path, monkeypatch, valid):
    content = b"Local inference source"
    document = SimpleNamespace(
        id=uuid.uuid4(), storage_path="test/source.txt",
        checksum_sha256=hashlib.sha256(content if valid else b"other").hexdigest(),
        status="uploaded", error_message=None,
    )
    db = Mock()
    db.get.return_value = document
    blob = Mock()
    blob.download_bytes.return_value = content
    monkeypatch.setattr(ingestion, "get_azure_blob_storage", lambda: blob)
    monkeypatch.setattr(ingestion.settings, "storage_backend", "azure_blob")
    monkeypatch.setattr(ingestion, "storage", StorageManager(root=tmp_path, max_upload_size_mb=25))
    parser = Mock(side_effect=RuntimeError("parser reached"))
    monkeypatch.setattr(ingestion, "parse_document", parser)
    with pytest.raises((RuntimeError, ValueError), match="parser reached" if valid else "checksum"):
        ingestion.extract_stored_document(db, document.id)
    path = tmp_path / document.storage_path
    if valid:
        assert path.read_bytes() == content
        parser.assert_called_once()
    else:
        assert not path.exists()
        parser.assert_not_called()
    assert not list(tmp_path.rglob("*.tmp"))
