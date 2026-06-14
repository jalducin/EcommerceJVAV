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
    # Click & collect: recoger en tienda
    pickup_enabled: bool = True
    pickup_locations: list[dict] = Field(
        default_factory=lambda: [
            {
                "id": "cdmx-centro",
                "name": "JV Market — CDMX Centro",
                "address": "Av. Juárez 100, Centro, CDMX",
            },
            {
                "id": "gdl-andares",
                "name": "JV Market — Guadalajara Andares",
                "address": "Blvd. Puerta de Hierro 4965, Zapopan",
            },
        ]
    )
    # Tokens de tema (CSS Custom Properties); por defecto, azul metálico suave.
    theme: dict[str, str] = Field(
        default_factory=lambda: {
            "silver": "#AEB9C7",
            "gold": "#5B8DD6",
            "steel": "#3E5C76",
            "copper": "#7FA8D4",
            "chrome": "#E6ECF3",
            "dark-metal": "#16202E",
        }
    )
