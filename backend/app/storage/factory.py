from functools import lru_cache

from app.core.config import settings

from app.storage.azure_blob import (
    AzureBlobStorage,
)


@lru_cache
def get_azure_blob_storage():

    if (
        settings.storage_backend
        != "azure_blob"
    ):

        raise RuntimeError(
            "Azure Blob Storage is "
            "not active."
        )


    return AzureBlobStorage()