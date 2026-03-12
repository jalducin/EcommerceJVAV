from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..dependencies import require_admin
from ..schemas.product import ProductCreate, ProductList, ProductResponse, ProductUpdate
from ..services.products import (
    create_product,
    delete_product,
    get_product,
    get_products,
    update_product,
)

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=ProductList)
async def list_products(
    limit: int = Query(20, ge=1, le=100, description="Número de resultados por página"),
    offset: int = Query(0, ge=0, description="Número de resultados a saltar"),
    category: str | None = Query(None, description="Filtrar por categoría"),
    search: str | None = Query(None, description="Buscar por nombre"),
    min_price: float | None = Query(None, ge=0, description="Precio mínimo"),
    max_price: float | None = Query(None, ge=0, description="Precio máximo"),
    db: AsyncSession = Depends(get_db),
):
    """Catálogo público de productos con filtros y paginación."""
    items, total = await get_products(db, limit, offset, category, search, min_price, max_price)
    return ProductList(items=items, total=total, limit=limit, offset=offset)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product_detail(product_id: int, db: AsyncSession = Depends(get_db)):
    """Detalle de un producto por ID."""
    return await get_product(db, product_id)


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_new_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_admin),
):
    """Crear producto (solo admin)."""
    return await create_product(db, data)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_existing_product(
    product_id: int,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_admin),
):
    """Actualizar producto parcialmente (solo admin)."""
    return await update_product(db, product_id, data)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def soft_delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_admin),
):
    """Soft delete de producto — marca is_active=False (solo admin)."""
    await delete_product(db, product_id)
