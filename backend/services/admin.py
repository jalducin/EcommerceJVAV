from datetime import date, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.order import Order
from ..models.product import Product
from ..models.user import User
from ..schemas.admin import AdminOrderList, DashboardStats, DailySale, OrderStatusUpdate
from ..schemas.order import OrderResponse


async def get_dashboard_stats(db: AsyncSession) -> DashboardStats:
    """Calcula y devuelve las estadísticas para el dashboard de admin."""
    today = date.today()
    start_of_day = datetime.combine(today, datetime.min.time())

    # Ventas y órdenes de hoy
    sales_today_query = select(func.sum(Order.total), func.count(Order.id)).where(
        Order.created_at >= start_of_day
    )
    sales_res = await db.execute(sales_today_query)
    sales_today, orders_today = sales_res.one_or_none() or (0, 0)

    # Órdenes pendientes
    pending_orders_query = select(func.count(Order.id)).where(Order.status == "pending")
    pending_orders = await db.scalar(pending_orders_query)

    # Estadísticas de productos
    low_stock_query = select(func.count(Product.id)).where(Product.stock > 0, Product.stock < 5)
    low_stock_count = await db.scalar(low_stock_query)

    out_of_stock_query = select(func.count(Product.id)).where(Product.stock == 0)
    out_of_stock_count = await db.scalar(out_of_stock_query)

    total_products_query = select(func.count(Product.id))
    total_products = await db.scalar(total_products_query)

    # Estadísticas de usuarios
    total_users_query = select(func.count(User.id)).where(User.role == "client")
    total_users = await db.scalar(total_users_query)

    # Ventas de los últimos 7 días para la gráfica
    sales_last_7_days_data = []
    seven_days_ago = today - timedelta(days=6)

    sales_by_day_query = (
        select(
            func.date(Order.created_at).label("sale_date"),
            func.sum(Order.total).label("daily_total"),
        )
        .where(func.date(Order.created_at) >= seven_days_ago)
        .group_by(func.date(Order.created_at))
        .order_by(func.date(Order.created_at))
    )
    sales_by_day_res = await db.execute(sales_by_day_query)
    sales_map = {row.sale_date: row.daily_total for row in sales_by_day_res.all()}

    for i in range(7):
        current_date = seven_days_ago + timedelta(days=i)
        day_str = current_date.strftime("%a").capitalize()
        sales_last_7_days_data.append(
            DailySale(date=day_str, total=sales_map.get(current_date, 0.0))
        )

    return DashboardStats(
        sales_today=sales_today or 0.0,
        orders_today=orders_today or 0,
        orders_pending=pending_orders or 0,
        products_low_stock=low_stock_count or 0,
        products_out_stock=out_of_stock_count or 0,
        total_products=total_products or 0,
        total_users=total_users or 0,
        sales_last_7_days=sales_last_7_days_data,
    )


async def get_admin_orders(
    db: AsyncSession, limit: int, offset: int, status: str | None
) -> AdminOrderList:
    """Obtiene todos los pedidos con paginación y filtro."""
    query = select(Order).options(selectinload(Order.user)).order_by(Order.created_at.desc())
    count_query = select(func.count(Order.id))

    if status:
        query = query.where(Order.status == status)
        count_query = count_query.where(Order.status == status)

    total = await db.scalar(count_query)
    result = await db.execute(query.limit(limit).offset(offset))
    orders = result.scalars().all()

    return AdminOrderList(items=orders, total=total or 0)


async def update_order_status(db: AsyncSession, order_id: int, data: OrderStatusUpdate):
    """Actualiza el estado de un pedido."""
    order = await db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")

    order.status = data.status
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order