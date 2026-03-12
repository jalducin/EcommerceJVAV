from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..dependencies import get_current_user
from ..schemas.order import CheckoutRequest, OrderDetail, OrderResponse
from ..services.orders import checkout, get_order_detail, get_user_orders

router = APIRouter(prefix="/api/orders", tags=["orders"])


def _uid(user: dict) -> int:
    return int(user["sub"])


@router.post("/checkout", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    data: CheckoutRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Crear pedido desde el carrito:
    - Valida stock de todos los ítems
    - Crea la orden y los OrderItems
    - Descuenta inventario
    - Vacía el carrito
    """
    return await checkout(db, _uid(current_user), data)


@router.get("", response_model=list[OrderResponse])
async def list_orders(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Historial de pedidos del usuario autenticado."""
    return await get_user_orders(db, _uid(current_user))


@router.get("/{order_id}", response_model=OrderDetail)
async def get_order(
    order_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Detalle de un pedido con sus ítems."""
    return await get_order_detail(db, _uid(current_user), order_id)
