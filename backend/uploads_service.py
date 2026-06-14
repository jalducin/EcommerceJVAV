"""Generación de URLs prefirmadas (PUT) para subir imágenes de producto a S3."""

from __future__ import annotations

import uuid

import boto3

from backend.config import settings

# Tipos de imagen permitidos y su extensión canónica.
ALLOWED_CONTENT_TYPES: dict[str, str] = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/avif": "avif",
}

PREFIX = "media"
EXPIRES_SECONDS = 300


class UploadConfigError(RuntimeError):
    """El bucket de media no está configurado en el entorno."""


def is_allowed(content_type: str) -> bool:
    return content_type in ALLOWED_CONTENT_TYPES


def _public_base() -> str:
    base = settings.MEDIA_PUBLIC_BASE or ""
    return base.rstrip("/")


def generate_presigned_upload(filename: str, content_type: str) -> dict[str, str]:
    """Devuelve {upload_url, public_url, key} para un PUT prefirmado bajo media/.

    Lanza ValueError si el tipo no es de imagen y UploadConfigError si falta el bucket.
    """
    if not is_allowed(content_type):
        raise ValueError(f"Tipo de archivo no permitido: {content_type}")
    if not settings.MEDIA_BUCKET:
        raise UploadConfigError("MEDIA_BUCKET no está configurado")

    ext = ALLOWED_CONTENT_TYPES[content_type]
    key = f"{PREFIX}/{uuid.uuid4().hex}.{ext}"

    client = boto3.client("s3", region_name=settings.AWS_REGION)
    upload_url = client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": settings.MEDIA_BUCKET,
            "Key": key,
            "ContentType": content_type,
        },
        ExpiresIn=EXPIRES_SECONDS,
    )
    public_url = f"{_public_base()}/{key}" if _public_base() else key
    return {"upload_url": upload_url, "public_url": public_url, "key": key}
