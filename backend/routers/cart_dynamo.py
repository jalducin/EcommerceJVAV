"""Endpoints de carrito (DynamoDB)."""

from __future__ import annotations

from fastapi import APIRouter, Body, Depends

from backend.cart_service import build_cart_view
from backend.deps import get_current_user
from backend.repositories import cart_repo
from backend.schemas.checkout import CartItemIn, CartSync, CartView

router = APIRouter(prefix="/api/cart", tags=["cart"])


@router.get("", response_model=CartView)
def get_cart(user: dict = Depends(get_current_user)) -> CartView:
    return build_cart_view(user["id"])


@router.post("/items", response_model=CartView)
def add_item(item: CartItemIn, user: dict = Depends(get_current_user)) -> CartView:
    cart_repo.add_item(user["id"], item)
    return build_cart_view(user["id"])


@router.put("/items/{product_id}/{sku}", response_model=CartView)
def update_item(
    product_id: str,
    sku: str,
    quantity: int = Body(embed=True),
    user: dict = Depends(get_current_user),
) -> CartView:
    cart_repo.set_quantity(user["id"], product_id, sku, quantity)
    return build_cart_view(user["id"])


@router.delete("/items/{product_id}/{sku}", response_model=CartView)
def delete_item(
    product_id: str, sku: str, user: dict = Depends(get_current_user)
) -> CartView:
    cart_repo.delete_item(user["id"], product_id, sku)
    return build_cart_view(user["id"])


@router.post("/sync", response_model=CartView)
def sync_cart(data: CartSync, user: dict = Depends(get_current_user)) -> CartView:
    cart_repo.sync(user["id"], data.items)
    return build_cart_view(user["id"])
