from pydantic import BaseModel
from typing import List

from .order import OrderResponse


class DailySale(BaseModel):
    date: str
    total: float


class DashboardStats(BaseModel):
    sales_today: float
    orders_today: int
    orders_pending: int
    products_low_stock: int
    products_out_stock: int
    total_products: int
    total_users: int
    sales_last_7_days: List[DailySale]


class OrderStatusUpdate(BaseModel):
    status: str


class AdminOrderList(BaseModel):
    items: List[OrderResponse]
    total: int