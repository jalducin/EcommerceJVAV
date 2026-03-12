from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class CheckoutAddress(BaseModel):
    full_name: str
    street: str
    city: str
    state: str
    postal_code: str
    country: str = "México"
    phone: str

    @field_validator("full_name", "street", "city", "state", "postal_code", "phone")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Este campo es obligatorio")
        return v.strip()


class CheckoutRequest(BaseModel):
    shipping_address: CheckoutAddress
    payment_method: str = "card"

    @field_validator("payment_method")
    @classmethod
    def valid_payment(cls, v: str) -> str:
        if v not in ("card", "cash"):
            raise ValueError("Método de pago inválido. Use 'card' o 'cash'")
        return v


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity: int
    unit_price: float


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    total: float
    shipping_address: dict | None
    created_at: datetime


class OrderDetail(OrderResponse):
    items: list[OrderItemResponse]
