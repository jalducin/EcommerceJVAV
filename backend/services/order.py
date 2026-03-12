from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from ..models.cart import CartItem
from ..models.order import Order, OrderItem
from ..models.product import Product
from ..models.user import User
from ..schemas.order import CheckoutRequest, OrderDetail
from ..utils.email import send_order_confirmation_email


async def create_order_from_cart(db: AsyncSession, user: User, data: CheckoutRequest) -> Order:
    """
    Crea un pedido desde el carrito, valida stock, descuenta inventario,
    limpia el carrito y dispara el email de confirmación.
    """
    async with db.begin_nested():
        cart_items_stmt = (
            select(CartItem).where(CartItem.user_id == user.id).options(selectinload(CartItem.product))
        )
        cart_items_res = await db.execute(cart_items_stmt)
        cart_items = cart_items_res.scalars().all()

        if not cart_items:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El carrito está vacío")

        total = 0
        order_items_to_create = []

        product_ids = [item.product_id for item in cart_items]
        await db.execute(select(Product).where(Product.id.in_(product_ids)).with_for_update())

        for item in cart_items:
            if item.product.stock < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Stock insuficiente para '{item.product.name}'. Disponible: {item.product.stock}",
                )
            item.product.stock -= item.quantity
            db.add(item.product)

            total += item.quantity * item.product.price
            order_items_to_create.append(
                OrderItem(product_id=item.product_id, quantity=item.quantity, unit_price=item.product.price)
            )

        new_order = Order(
            user_id=user.id,
            total=total,
            shipping_address=data.shipping_address.model_dump() if data.shipping_address else None,
        )
        new_order.items.extend(order_items_to_create)
        db.add(new_order)

        for item in cart_items:
            await db.delete(item)

    await db.commit()
    await db.refresh(new_order)

    # Recargar la orden con todas las relaciones para el email y la respuesta
    final_order_stmt = (
        select(Order)
        .where(Order.id == new_order.id)
        .options(selectinload(Order.items).selectinload(OrderItem.product), selectinload(Order.user))
    )
    result = await db.execute(final_order_stmt)
    final_order = result.scalar_one()

    # Enviar email de confirmación
    try:
        order_detail_schema = OrderDetail.model_validate(final_order)
        await send_order_confirmation_email(email_to=user.email, order=order_detail_schema)
    except Exception as e:
        print(f"CRITICAL: El email para el pedido {final_order.id} no pudo ser enviado. Error: {e}")

    return final_order


async def get_user_orders(db: AsyncSession, user_id: int):
    stmt = select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_order_details(db: AsyncSession, order_id: int, user_id: int):
    stmt = (
        select(Order)
        .where(Order.id == order_id, Order.user_id == user_id)
        .options(selectinload(Order.items).selectinload(OrderItem.product))
    )
    order = await db.scalar(stmt)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")
    return order