"""Endpoints de catálogo de productos (DynamoDB, con variantes)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.deps import require_admin
from backend.repositories import product_repo, store_repo
from backend.schemas.catalog import Product, ProductCreate, ProductList, ProductUpdate

router = APIRouter(prefix="/api/products", tags=["products"])


def _validate_category(category: str) -> None:
    categories = store_repo.get_config().categories
    if categories and category not in categories:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Categoría inválida: {category}",
        )


@router.get("", response_model=ProductList)
def list_products(
    category: str | None = None,
    q: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    limit: int = Query(12, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> ProductList:
    return product_repo.list_products(
        category=category,
        q=q,
        min_price=min_price,
        max_price=max_price,
        limit=limit,
        offset=offset,
    )


@router.get("/{product_id}", response_model=Product)
def get_product(product_id: str) -> Product:
    product = product_repo.get_product(product_id)
    if not product or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado"
        )
    return product


@router.post("", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(
    data: ProductCreate, _admin: dict = Depends(require_admin)
) -> Product:
    _validate_category(data.category)
    return product_repo.create_product(data)


@router.put("/{product_id}", response_model=Product)
def update_product(
    product_id: str, data: ProductUpdate, _admin: dict = Depends(require_admin)
) -> Product:
    if data.category is not None:
        _validate_category(data.category)
    product = product_repo.update_product(product_id, data)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado"
        )
    return product


@router.delete(
    "/{product_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None
)
def delete_product(product_id: str, _admin: dict = Depends(require_admin)) -> None:
    if not product_repo.delete_product(product_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado"
        )
