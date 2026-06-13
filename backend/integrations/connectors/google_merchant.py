"""Conector de Google Merchant Center (Content API for Shopping). Sprint 4.

Canal **solo feed** (sin pedidos): capacidad CATALOG. Auth por cuenta de servicio/OAuth.
Un producto sin imagen se rechaza del feed (FeedItemError) sin abortar el lote.
"""

from __future__ import annotations

from backend.integrations.connector import Capability
from backend.integrations.connectors.channel_base import ChannelConnector
from backend.integrations.feeds import FeedItemError


class GoogleMerchantConnector(ChannelConnector):
    name = "google_merchant"
    capabilities = {Capability.CATALOG}  # feed puro, sin pedidos

    # Google verifica por cuenta de servicio/OAuth, no por webhook firmado.
    def verify_webhook(
        self, secret: str, raw_body: bytes, signature: str | None
    ) -> bool:
        return False

    def external_order_id(self, payload: dict) -> str:  # pragma: no cover - sin pedidos
        raise NotImplementedError("Google Merchant no ingiere pedidos")

    def to_canonical_order(self, payload: dict, canonical_id: str):  # pragma: no cover
        raise NotImplementedError("Google Merchant no ingiere pedidos")

    def to_feed_item(self, product) -> dict:
        if not product.images:
            raise FeedItemError("Producto sin imagen: requerido por Google Merchant")
        return {
            "offerId": product.id,
            "title": product.name,
            "description": product.description,
            "link": f"https://metalshop.example/product.html?id={product.id}",
            "imageLink": product.images[0],
            "availability": "in stock" if product.total_stock > 0 else "out of stock",
            "price": {"value": str(product.price), "currency": "MXN"},
            "productTypes": [product.category],
        }
