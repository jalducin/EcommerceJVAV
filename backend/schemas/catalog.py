"""Modelo de catálogo serverless: producto con variantes y atributos arbitrarios.

Business-agnostic: una variante lleva un mapa de atributos arbitrarios (talla, color,
capacidad, etc.) con su propio stock y ajuste de precio. Un producto puede no tener
variantes (stock a nivel de producto).
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class Variant(BaseModel):
    sku: str
    attrs: dict[str, str] = Field(
        default_factory=dict
    )  # p.ej. {"talla": "42", "color": "negro"}
    stock: int = 0
    price_delta: float = 0.0


class ProductCreate(BaseModel):
    name: str
    description: str = ""
    price: float = Field(gt=0)
    category: str
    images: list[str] = Field(default_factory=list)
    stock: int = 0  # usado solo si no hay variantes
    variants: list[Variant] = Field(default_factory=list)
    is_active: bool = True


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = Field(default=None, gt=0)
    category: str | None = None
    images: list[str] | None = None
    stock: int | None = None
    variants: list[Variant] | None = None
    is_active: bool | None = None


class Product(ProductCreate):
    id: str
    created_at: str

    @property
    def total_stock(self) -> int:
        if self.variants:
            return sum(v.stock for v in self.variants)
        return self.stock


class ProductList(BaseModel):
    items: list[Product]
    total: int
    limit: int
    offset: int
