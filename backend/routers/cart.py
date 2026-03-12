from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..dependencies import get_current_user
from ..schemas.cart import CartItemCreate, CartItemUpdate, CartResponse, CartSyncRequest
from ..services.cart import add_item, get_cart, remove_item, sync_cart, update_item

router = APIRouter(prefix="/api/cart", tags=["cart"])


def _uid(user: dict) -> int:
    return int(user["sub"])


@router.get("", response_model=CartResponse)
async def read_cart(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Carrito del usuario autenticado con totales."""
    return await get_cart(db, _uid(current_user))


@router.post("/items", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
async def add_cart_item(
    data: CartItemCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Agregar producto al carrito. Si ya existe, incrementa la cantidad."""
    await add_item(db, _uid(current_user), data)
    return await get_cart(db, _uid(current_user))


@router.put("/items/{item_id}", response_model=CartResponse)
async def update_cart_item(
    item_id: int,
    data: CartItemUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Actualizar cantidad de un ítem del carrito."""
    await update_item(db, _uid(current_user), item_id, data)
    return await get_cart(db, _uid(current_user))


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_cart_item(
    item_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Eliminar ítem del carrito."""
    await remove_item(db, _uid(current_user), item_id)


@router.post("/sync", response_model=CartResponse)
async def sync_cart_items(
    data: CartSyncRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Sincronizar carrito de localStorage con la BD al iniciar sesión."""
    return await sync_cart(db, _uid(current_user), data)
