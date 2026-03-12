from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..dependencies import require_admin
from ..schemas.admin import AdminOrderList, DashboardStats, OrderStatusUpdate
from ..schemas.order import OrderResponse
from ..services.admin import get_admin_orders, get_dashboard_stats, update_order_status

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/dashboard", response_model=DashboardStats)
async def dashboard(
    _: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Métricas del día: ventas, pedidos pendientes, productos con bajo stock."""
    return await get_dashboard_stats(db)


@router.get("/orders", response_model=AdminOrderList)
async def list_all_orders(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: str | None = Query(None, description="Filtrar por estado"),
    _: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Todos los pedidos del sistema con paginación y filtro opcional por estado."""
    return await get_admin_orders(db, limit, offset, status)


@router.patch("/orders/{order_id}/status", response_model=OrderResponse)
async def change_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    _: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Cambiar el estado de un pedido: pending → shipped → delivered | cancelled."""
    return await update_order_status(db, order_id, data)
