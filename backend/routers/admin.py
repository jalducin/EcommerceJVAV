"""Endpoints del panel de administración (serverless). Todos requieren rol admin."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from backend import admin_service
from backend.deps import require_admin
from backend.integrations.catalog_connectors import all_connectors

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
