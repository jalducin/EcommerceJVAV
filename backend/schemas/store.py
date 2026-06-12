"""Configuración de tienda (business-agnostic).

Controla marca, categorías, moneda, locale, impuestos/envío y tokens de tema. Cambiar
de negocio = cambiar esta configuración (y el dataset), sin tocar código.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class StoreConfig(BaseModel):
    name: str = "MetalShop"
    logo_url: str | None = None
    categories: list[str] = Field(default_factory=list)
    currency: str = "MXN"
    locale: str = "es-MX"
    tax_rate: float = 0.16  # 16% (IVA México) por defecto
    shipping_flat: float = 99.0
    free_shipping_threshold: float | None = None
    # Tokens de tema (CSS Custom Properties); por defecto, identidad metálica MetalShop.
    theme: dict[str, str] = Field(
        default_factory=lambda: {
            "silver": "#C0C0C0",
            "gold": "#D4AF37",
            "steel": "#4A5568",
            "copper": "#B87333",
            "chrome": "#E8E8E8",
            "dark-metal": "#1A1A2E",
        }
    )
