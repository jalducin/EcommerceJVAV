"""Cálculo de totales según la configuración de tienda (impuesto/envío/moneda)."""

from __future__ import annotations

from backend.schemas.store import StoreConfig


def compute_totals(subtotal: float, config: StoreConfig) -> dict:
    """Devuelve subtotal, impuesto, envío y total según la configuración vigente."""
    tax = round(subtotal * config.tax_rate, 2)
    if (
        config.free_shipping_threshold is not None
        and subtotal >= config.free_shipping_threshold
    ):
        shipping = 0.0
    else:
        shipping = config.shipping_flat if subtotal > 0 else 0.0
    total = round(subtotal + tax + shipping, 2)
    return {
        "subtotal": round(subtotal, 2),
        "tax": tax,
        "shipping": round(shipping, 2),
        "total": total,
        "currency": config.currency,
    }
