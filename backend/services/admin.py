from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.order import Order
from ..models.product import Product
from ..models.user import User
from ..schemas.admin import (
    AdminOrderList,
    AdminOrderResponse,
    DashboardStats,
    OrderStatusUpdate,
)


async def get_dashboard_stats(db: AsyncSession) -> DashboardStats:
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end   = today_start + timedelta(days=1)

    # Ventas hoy (órdenes no canceladas)
    sales_today_row = await db.execute(
        select(func.sum(Order.total)).where(
            Order.created_at >= today_start,
            Order.created_at < today_end,
            Order.status != "cancelled",
        )
    )
    sales_today = float(sales_today_row.scalar_one() or 0)

    # Órdenes hoy
    orders_today = (
        await db.execute(
            select(func.count(Order.id)).where(
                Order.created_at >= today_start, Order.created_at < today_end
            )
        )
    ).scalar_one()

    # Órdenes pendientes
    orders_pending = (
        await db.execute(select(func.count(Order.id)).where(Order.status == "pending"))
    ).scalar_one()

    # Productos con stock bajo (1–4)
    products_low_stock = (
        await db.execute(
            select(func.count(Product.id)).where(
                Product.is_active == True,  # noqa: E712
                Product.stock < 5,
                Product.stock > 0,
            )
        )
    ).scalar_one()

    # Productos sin stock
    products_out_stock = (
        await db.execute(
            select(func.count(Product.id)).where(
                Product.is_active == True, Product.stock == 0  # noqa: E712
            )
        )
    ).scalar_one()

    # Total productos activos
    total_products = (
        await db.execute(
            select(func.count(Product.id)).where(Product.is_active == True)  # noqa: E712
        )
    ).scalar_one()

    # Total usuarios
    total_users = (await db.execute(select(func.count(User.id)))).scalar_one()

    # Ventas últimos 7 días
    seven_days_ago = today_start - timedelta(days=6)
    sales_last_7_days: list[dict] = []
    for i in range(7):
        day_start = seven_days_ago + timedelta(days=i)
        day_end   = day_start + timedelta(days=1)
        result = await db.execute(
            select(func.sum(Order.total)).where(
                Order.created_at >= day_start,
                Order.created_at < day_end,
                Order.status != "cancelled",
            )
        )
        sales_last_7_days.append({
            "date":  day_start.strftime("%d/%m"),
            "total": float(result.scalar_one() or 0),
        })

    return DashboardStats(
        sales_today=sales_today,
        orders_today=orders_today,
        orders_pending=orders_pending,
        products_low_stock=products_low_stock,
        products_out_stock=products_out_stock,
        total_products=total_products,
        total_users=total_users,
        sales_last_7_days=sales_last_7_days,
    )


async def get_admin_orders(
    db: AsyncSession,
    limit: int = 20,
    offset: int = 0,
    status_filter: str | None = None,
) -> AdminOrderList:
    query = select(Order).options(selectinload(Order.user))
    if status_filter:
        query = query.where(Order.status == status_filter)

    count_q = select(func.count()).select_from(query.subquery())
    total   = (await db.execute(count_q)).scalar_one()

    result = await db.execute(
        query.order_by(Order.created_at.desc()).offset(offset).limit(limit)
    )
    orders = result.scalars().all()

    items = [
        AdminOrderResponse(
            id=o.id,
            user_id=o.user_id,
            user_email=o.user.email if o.user else None,
            status=o.status,
            total=o.total,
            shipping_address=o.shipping_address,
            created_at=o.created_at,
        )
        for o in orders
    ]
    return AdminOrderList(items=items, total=total, limit=limit, offset=offset)


async def update_order_status(
    db: AsyncSession, order_id: int, data: OrderStatusUpdate
) -> Order:
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orden no encontrada")
    order.status = data.status
    await db.flush()
    await db.refresh(order)
    return order
