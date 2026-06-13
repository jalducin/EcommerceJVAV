"""Generación de feeds de catálogo para canales tipo feed (Meta, TikTok, Google).

Un conector con capacidad de feed implementa `to_feed_item(product) -> dict` y puede
lanzar FeedItemError para un producto inválido; el lote no se aborta: el error se
reporta por producto (observabilidad) y el resto se publica.
"""

from __future__ import annotations


class FeedItemError(Exception):
    """Un producto no cumple los requisitos del feed del canal."""


def build_feed(connector, products: list) -> dict:
    """Construye el feed; devuelve items válidos y errores por producto."""
    items: list[dict] = []
    errors: list[dict] = []
    for product in products:
        try:
            items.append(connector.to_feed_item(product))
        except FeedItemError as exc:
            errors.append(
                {"product_id": getattr(product, "id", None), "error": str(exc)}
            )
    return {
        "items": items,
        "errors": errors,
        "count": len(items),
        "rejected": len(errors),
    }
