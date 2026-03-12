from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..dependencies import get_current_user
from ..models.user import User
from ..schemas.order import CheckoutRequest, OrderDetail, OrderResponse
from ..services import order as order_service

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("/checkout", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def checkout(
    data: CheckoutRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Crea un pedido desde el carrito, valida stock, descuenta inventario,
    limpia el carrito y envía un email de confirmación.
    """
    order = await order_service.create_order_from_cart(db, current_user, data)
    return order


@router.get("", response_model=List[OrderResponse])
async def get_my_orders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene el historial de pedidos del usuario autenticado."""
    return await order_service.get_user_orders(db, current_user.id)


@router.get("/{order_id}", response_model=OrderDetail)
async def get_single_order(
    order_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Obtiene el detalle de un pedido específico del usuario autenticado."""
    return await order_service.get_order_details(db, order_id, current_user.id)