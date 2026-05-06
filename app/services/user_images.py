from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

from azure.core.exceptions import AzureError
from azure.storage.blob import BlobServiceClient, ContentSettings
from fastapi import HTTPException, UploadFile, status
from PIL import Image, ImageOps

from app.core.config import settings
from app.models.user import User


USER_IMAGE_PLACEHOLDER_PATH = "assets/placeholders/user.jpg"
USER_IMAGE_SIZE = 512
USER_IMAGE_QUALITY = 82
USER_IMAGE_ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}


def get_user_image_url(user: User | None) -> str:
    if user and user.image_url:
        return user.image_url

    return USER_IMAGE_PLACEHOLDER_PATH


def _build_blob_name(user_id: int, filename: str | None) -> str:
    extension = Path(filename or "avatar.jpg").suffix.lower() or ".jpg"
    if extension not in {".jpg", ".jpeg"}:
        extension = ".jpg"
    return f"user-images/{user_id}/{uuid4().hex}{extension}"


def _optimize_image(file: UploadFile) -> bytes:
    content_type = (file.content_type or "").lower()
    if content_type not in USER_IMAGE_ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported image format. Use JPG, PNG or WEBP.",
        )

    try:
        file.file.seek(0)
        image = Image.open(file.file)
        image = ImageOps.exif_transpose(image)
        image = image.convert("RGB")
        image = ImageOps.fit(image, (USER_IMAGE_SIZE, USER_IMAGE_SIZE), method=Image.Resampling.LANCZOS)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to read the provided image.",
        ) from exc

    output = BytesIO()
    image.save(output, format="JPEG", quality=USER_IMAGE_QUALITY, optimize=True)
    return output.getvalue()


def upload_user_image(file: UploadFile, user_id: int) -> str:
    if not settings.azure_storage_connection_string:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Azure Blob Storage is not configured for uploads.",
        )

    if not settings.azure_storage_container_name:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Azure Blob Storage container is not configured.",
        )

    optimized_image = _optimize_image(file)
    blob_name = _build_blob_name(user_id=user_id, filename=file.filename)

    try:
        blob_service = BlobServiceClient.from_connection_string(settings.azure_storage_connection_string)
        blob_client = blob_service.get_blob_client(container=settings.azure_storage_container_name, blob=blob_name)
        blob_client.upload_blob(
            optimized_image,
            overwrite=True,
            content_settings=ContentSettings(content_type="image/jpeg", cache_control="public, max-age=31536000"),
        )
    except AzureError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to upload user image to Azure Blob Storage.",
        ) from exc

    return blob_client.url


def delete_user_image_by_url(image_url: str) -> None:
    if not image_url or not settings.azure_storage_connection_string or not settings.azure_storage_container_name:
        return

    parsed = urlparse(image_url)
    blob_prefix = f"/{settings.azure_storage_container_name}/"
    if blob_prefix not in parsed.path:
        return

    blob_name = parsed.path.split(blob_prefix, maxsplit=1)[1]
    if not blob_name:
        return

    try:
        blob_service = BlobServiceClient.from_connection_string(settings.azure_storage_connection_string)
        blob_client = blob_service.get_blob_client(container=settings.azure_storage_container_name, blob=blob_name)
        blob_client.delete_blob(delete_snapshots="include")
    except AzureError:
        return