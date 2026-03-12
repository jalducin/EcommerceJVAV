from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.cart import CartItem
from ..models.product import Product
from ..schemas.cart import CartItemCreate, CartItemUpdate, CartResponse, CartSyncRequest


async def get_cart(db: AsyncSession, user_id: int) -> CartResponse:
    result = await db.execute(
        select(CartItem)
        .where(CartItem.user_id == user_id)
        .options(selectinload(CartItem.product))
        .order_by(CartItem.id)
    )
    items = result.scalars().all()

    subtotal = round(
        sum(item.product.price * item.quantity for item in items if item.product), 2
    )
    return CartResponse(
        items=items,
        subtotal=subtotal,
        total=subtotal,
        item_count=sum(item.quantity for item in items),
    )


async def _get_active_product(db: AsyncSession, product_id: int) -> Product:
    product = await db.get(Product, product_id)
    if not product or not product.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return product


async def add_item(db: AsyncSession, user_id: int, data: CartItemCreate) -> None:
    product = await _get_active_product(db, data.product_id)

    result = await db.execute(
        select(CartItem).where(
            CartItem.user_id == user_id,
            CartItem.product_id == data.product_id,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        new_qty = existing.quantity + data.quantity
        if new_qty > product.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock insuficiente. Disponible: {product.stock}",
            )
        existing.quantity = new_qty
    else:
        if data.quantity > product.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock insuficiente. Disponible: {product.stock}",
            )
        db.add(CartItem(user_id=user_id, product_id=data.product_id, quantity=data.quantity))

    await db.flush()


async def update_item(db: AsyncSession, user_id: int, item_id: int, data: CartItemUpdate) -> None:
    result = await db.execute(
        select(CartItem).where(CartItem.id == item_id, CartItem.user_id == user_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item no encontrado")

    product = await _get_active_product(db, item.product_id)
    if data.quantity > product.stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stock insuficiente. Disponible: {product.stock}",
        )
    item.quantity = data.quantity
    await db.flush()


async def remove_item(db: AsyncSession, user_id: int, item_id: int) -> None:
    result = await db.execute(
        select(CartItem).where(CartItem.id == item_id, CartItem.user_id == user_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item no encontrado")
    await db.delete(item)
    await db.flush()


async def sync_cart(db: AsyncSession, user_id: int, data: CartSyncRequest) -> CartResponse:
    """Fusiona carrito de localStorage con la BD al iniciar sesión."""
    for sync_item in data.items:
        product = await db.get(Product, sync_item.product_id)
        if not product or not product.is_active or product.stock == 0:
            continue

        result = await db.execute(
            select(CartItem).where(
                CartItem.user_id == user_id,
                CartItem.product_id == sync_item.product_id,
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.quantity = min(
                max(existing.quantity, sync_item.quantity), product.stock
            )
        else:
            db.add(
                CartItem(
                    user_id=user_id,
                    product_id=sync_item.product_id,
                    quantity=min(sync_item.quantity, product.stock),
                )
            )
        await db.flush()

    return await get_cart(db, user_id)
