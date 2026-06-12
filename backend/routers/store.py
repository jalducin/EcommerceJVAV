"""Endpoint de configuración de tienda (business-agnostic)."""

from __future__ import annotations

from fastapi import APIRouter

from backend.repositories import store_repo
from backend.schemas.store import StoreConfig

router = APIRouter(prefix="/api", tags=["config"])


@router.get("/config", response_model=StoreConfig)
def get_store_config() -> StoreConfig:
    return store_repo.get_config()
