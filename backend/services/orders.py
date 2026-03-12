from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.cart import CartItem
from ..models.order import Order, OrderItem
from ..schemas.order import CheckoutRequest


async def checkout(db: AsyncSession, user_id: int, data: CheckoutRequest) -> Order:
    # Cargar carrito con productos
    result = await db.execute(
        select(CartItem)
        .where(CartItem.user_id == user_id)
        .options(selectinload(CartItem.product))
    )
    cart_items = result.scalars().all()

    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El carrito está vacío",
        )

    # Validar stock de cada ítem
    for item in cart_items:
        if not item.product or not item.product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El producto ID {item.product_id} ya no está disponible",
            )
        if item.product.stock < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Stock insuficiente para '{item.product.name}'. "
                    f"Solicitado: {item.quantity}, disponible: {item.product.stock}"
                ),
            )

    total = round(sum(item.product.price * item.quantity for item in cart_items), 2)

    # Crear la orden
    order = Order(
        user_id=user_id,
        total=total,
        shipping_address=data.shipping_address.model_dump(),
        status="pending",
    )
    db.add(order)
    await db.flush()  # Obtener order.id

    # Crear ítems de la orden y descontar stock
    for item in cart_items:
        db.add(
            OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.product.price,
            )
        )
        item.product.stock -= item.quantity

    # Vaciar carrito
    for item in cart_items:
        await db.delete(item)

    await db.flush()
    await db.refresh(order)
    return order


async def get_user_orders(db: AsyncSession, user_id: int) -> list[Order]:
    result = await db.execute(
        select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
    )
    return result.scalars().all()  # type: ignore[return-value]


async def get_order_detail(db: AsyncSession, user_id: int, order_id: int) -> Order:
    result = await db.execute(
        select(Order)
        .where(Order.id == order_id, Order.user_id == user_id)
        .options(selectinload(Order.items))
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orden no encontrada")
    return order
