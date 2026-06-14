"""Endpoints de lista de deseos (requieren autenticación)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from backend.deps import get_current_user
from backend.repositories import product_repo, wishlist_repo
from backend.schemas.catalog import Product

router = APIRouter(prefix="/api/wishlist", tags=["wishlist"])


@router.get("", response_model=list[Product])
def my_wishlist(user: dict = Depends(get_current_user)) -> list[Product]:
    productos = []
    for pid in wishlist_repo.list_product_ids(user["id"]):
        p = product_repo.get_product(pid)
        if p and p.is_active:
            productos.append(p)
    return productos


@router.post(
    "/{product_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None
)
def add_to_wishlist(product_id: str, user: dict = Depends(get_current_user)) -> None:
    wishlist_repo.add(user["id"], product_id)


@router.delete(
    "/{product_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None
)
def remove_from_wishlist(
    product_id: str, user: dict = Depends(get_current_user)
) -> None:
    wishlist_repo.remove(user["id"], product_id)
