from datetime import UTC, datetime
import mimetypes
from pathlib import Path
from uuid import uuid4

from azure.core.exceptions import AzureError
from azure.storage.blob import BlobServiceClient, ContentSettings
from fastapi import HTTPException, UploadFile, status

from app.core.config import settings


def _build_blob_name(slug: str, asset_field: str, filename: str | None, content_type: str | None) -> str:
    extension = Path(filename or "upload").suffix.lower()
    if not extension:
        extension = mimetypes.guess_extension(content_type or "") or ".bin"

    timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    return f"system-settings/{slug}/{asset_field}/{timestamp}-{uuid4().hex}{extension}"


def upload_system_settings_asset(file: UploadFile, slug: str, asset_field: str) -> str:
    if not settings.azure_storage_connection_string:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Azure Blob Storage is not configured for image uploads.",
        )

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image uploads are supported for system settings assets.",
        )

    container_name = settings.azure_storage_container_name.strip()
    if not container_name:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Azure Blob Storage container is not configured.",
        )

    blob_service_client = BlobServiceClient.from_connection_string(settings.azure_storage_connection_string)
    blob_name = _build_blob_name(slug, asset_field, file.filename, file.content_type)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    try:
        file.file.seek(0)
        blob_client.upload_blob(
            file.file,
            overwrite=True,
            content_settings=ContentSettings(
                content_type=file.content_type,
                cache_control="public, max-age=31536000",
            ),
        )
    except AzureError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to upload image to Azure Blob Storage.",
        ) from exc

    return blob_client.url