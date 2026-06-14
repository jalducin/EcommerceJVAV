"""Endpoints del panel de administración (serverless). Todos requieren rol admin."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from backend import admin_service, category_service, uploads_service
from backend.deps import require_admin
from backend.integrations.catalog_connectors import all_connectors
from backend.schemas.admin_media import (
    CategoryCreate,
    CategoryList,
    PresignRequest,
    PresignResponse,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/dashboard")
def dashboard(_admin: dict = Depends(require_admin)) -> dict:
    return admin_service.dashboard()


@router.get("/orders")
def orders(_admin: dict = Depends(require_admin)) -> list[dict]:
    return admin_service.unified_orders()


@router.patch("/orders/channel/{canonical_id}/status")
def set_channel_status(
    canonical_id: str, new_status: str, _admin: dict = Depends(require_admin)
) -> dict:
    if not admin_service.set_channel_order_status(canonical_id, new_status):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado"
        )
    return {"id": canonical_id, "status": new_status}


@router.get("/connectors")
def connectors(_admin: dict = Depends(require_admin)) -> list[dict]:
    return all_connectors()


# ── Categorías ────────────────────────────────────────────────────────────────


@router.get(
    "/categories",
    response_model=CategoryList,
    summary="Listar categorías de la tienda",
    description="Devuelve las categorías declaradas en la configuración de tienda.",
)
def list_categories(_admin: dict = Depends(require_admin)) -> CategoryList:
    return CategoryList(categories=category_service.list_categories())


@router.post(
    "/categories",
    response_model=CategoryList,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar una categoría",
    description=(
        "Agrega una categoría a la tienda. Idempotente: si ya existe "
        "(ignorando mayúsculas y espacios) no la duplica."
    ),
)
def add_category(
    data: CategoryCreate, _admin: dict = Depends(require_admin)
) -> CategoryList:
    return CategoryList(categories=category_service.add_category(data.name))


@router.delete(
    "/categories/{name}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Eliminar una categoría",
    description=(
        "Elimina una categoría de la tienda. Responde 409 si algún producto "
        "activo la usa."
    ),
    responses={409: {"description": "Categoría en uso por productos activos"}},
)
def remove_category(name: str, _admin: dict = Depends(require_admin)) -> None:
    if category_service.category_in_use(name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La categoría está en uso por productos activos",
        )
    category_service.remove_category(name)


# ── Subida de imágenes (presigned PUT) ──────────────────────────────────────────


@router.post(
    "/uploads/presign",
    response_model=PresignResponse,
    summary="Generar URL prefirmada para subir una imagen",
    description=(
        "Devuelve una URL PUT prefirmada hacia el prefijo `media/` del bucket de "
        "frontend y la URL pública (CloudFront) resultante. Solo acepta tipos de "
        "imagen (jpeg, png, webp, avif)."
    ),
    responses={
        422: {"description": "Tipo de archivo no permitido"},
        503: {"description": "Subida de imágenes no configurada en el entorno"},
    },
)
def presign_upload(
    data: PresignRequest, _admin: dict = Depends(require_admin)
) -> PresignResponse:
    try:
        result = uploads_service.generate_presigned_upload(
            data.filename, data.content_type
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    except uploads_service.UploadConfigError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
    return PresignResponse(**result)
