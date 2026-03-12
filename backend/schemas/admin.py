from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class DashboardStats(BaseModel):
    sales_today: float
    orders_today: int
    orders_pending: int
    products_low_stock: int   # stock 1-4
    products_out_stock: int   # stock 0
    total_products: int
    total_users: int
    sales_last_7_days: list[dict]  # [{"date": "05/03", "total": 450.0}, ...]


class AdminOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    user_email: str | None
    status: str
    total: float
    shipping_address: dict | None
    created_at: datetime


class AdminOrderList(BaseModel):
    items: list[AdminOrderResponse]
    total: int
    limit: int
    offset: int


class OrderStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def valid_status(cls, v: str) -> str:
        valid = {"pending", "shipped", "delivered", "cancelled"}
        if v not in valid:
            raise ValueError(f"Estado inválido. Valores válidos: {', '.join(sorted(valid))}")
        return v
