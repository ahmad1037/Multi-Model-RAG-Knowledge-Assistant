from azure.storage.blob import (
    BlobServiceClient,
    ContentSettings,
)

from app.core.config import settings


class AzureBlobStorage:

    def __init__(self):

        connection_string = (
            settings
            .azure_storage_connection_string
        )

        if not connection_string:

            raise RuntimeError(
                "AZURE_STORAGE_CONNECTION_STRING "
                "is not configured."
            )


        service = (
            BlobServiceClient
            .from_connection_string(
                connection_string
            )
        )


        self.container = (
            service
            .get_container_client(
                settings
                .azure_storage_container
            )
        )


    def upload_bytes(
        self,
        *,
        blob_name: str,
        data: bytes,
        content_type: str | None,
    ) -> None:

        blob = (
            self.container
            .get_blob_client(
                blob_name
            )
        )


        blob.upload_blob(
            data,

            overwrite=True,

            content_settings=(
                ContentSettings(
                    content_type=(
                        content_type
                    )
                )
            ),
        )


    def download_bytes(
        self,
        blob_name: str,
    ) -> bytes:

        blob = (
            self.container
            .get_blob_client(
                blob_name
            )
        )


        return (
            blob
            .download_blob()
            .readall()
        )


    def exists(
        self,
        blob_name: str,
    ) -> bool:

        blob = (
            self.container
            .get_blob_client(
                blob_name
            )
        )

        return blob.exists()