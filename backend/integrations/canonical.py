"""Modelo canónico de integración (independiente de proveedor).

Cada conector traduce entre el modelo de su proveedor y estas entidades. Son
deliberadamente neutrales: ningún campo es específico de Shopify, Amazon, etc.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class EntityType(str, Enum):
    PRODUCT = "product"
    INVENTORY = "inventory"
    ORDER = "order"
    CUSTOMER = "customer"
    PAYMENT = "payment"


class CanonicalVariant(BaseModel):
    sku: str
    attrs: dict[str, str] = Field(default_factory=dict)
    price: float = 0.0
    stock: int = 0


class CanonicalProduct(BaseModel):
    canonical_id: str
    name: str
    description: str = ""
    category: str = ""
    price: float = 0.0
    images: list[str] = Field(default_factory=list)
    variants: list[CanonicalVariant] = Field(default_factory=list)


class InventoryLevel(BaseModel):
    canonical_product_id: str
    sku: str = "-"
    available: int = 0
    location: str = "default"


class CanonicalOrderLine(BaseModel):
    sku: str = "-"
    name: str = ""
    unit_price: float = 0.0
    quantity: int = 1


class CanonicalOrder(BaseModel):
    canonical_id: str
    channel: str  # conector/canal de origen (shopify, mercadolibre, web, square…)
    external_id: str
    status: str = "pending"
    lines: list[CanonicalOrderLine] = Field(default_factory=list)
    total: float = 0.0
    currency: str = "MXN"
    customer_email: str | None = None


class CanonicalCustomer(BaseModel):
    canonical_id: str
    email: str
    full_name: str = ""
