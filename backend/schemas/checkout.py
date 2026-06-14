"""Schemas de carrito y pedidos para la app serverless."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CartItemIn(BaseModel):
    product_id: str
    sku: str = "-"  # sku de variante; "-" si el producto no tiene variantes
    quantity: int = Field(gt=0)


class CartSync(BaseModel):
    items: list[CartItemIn] = Field(default_factory=list)


class CartLine(BaseModel):
    product_id: str
    sku: str
    name: str
    unit_price: float
    quantity: int
    subtotal: float


class CartView(BaseModel):
    lines: list[CartLine]
    subtotal: float
    tax: float
    shipping: float
    total: float
    currency: str


class CheckoutRequest(BaseModel):
    shipping_address: dict = Field(default_factory=dict)
    fulfillment: str = "ship"  # "ship" (envío) | "pickup" (recoger en tienda)
    pickup_location_id: str | None = None


class OrderLine(BaseModel):
    product_id: str
    sku: str
    name: str
    unit_price: float
    quantity: int


class Order(BaseModel):
    id: str
    user_id: str
    status: str = "pending"
    channel: str = "web"
    lines: list[OrderLine]
    subtotal: float
    tax: float
    shipping: float
    total: float
    currency: str
    shipping_address: dict = Field(default_factory=dict)
    fulfillment: str = "ship"
    pickup_location: dict | None = None
    created_at: str
