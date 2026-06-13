"""Conector de Meta Commerce (Facebook/Instagram Shop). Sprint 4.

Capacidades: catálogo (feed) y pedidos donde haya checkout nativo. Webhook firmado
por Meta con HMAC-SHA256 hex y prefijo 'sha256=' (header X-Hub-Signature-256).
"""

from __future__ import annotations

from backend.integrations.canonical import CanonicalOrder, CanonicalOrderLine
from backend.integrations.connector import Capability
from backend.integrations.connectors.channel_base import ChannelConnector
from backend.integrations.webhooks import verify_hmac_hex


class MetaConnector(ChannelConnector):
    name = "meta"
    capabilities = {Capability.CATALOG, Capability.ORDERS}
    webhook_signature_header = "X-Hub-Signature-256"

    def verify_webhook(
        self, secret: str, raw_body: bytes, signature: str | None
    ) -> bool:
        return verify_hmac_hex(secret, raw_body, signature, prefix="sha256=")

    def to_feed_item(self, product) -> dict:
        return {
            "id": product.id,
            "title": product.name,
            "description": product.description,
            "availability": "in stock" if product.total_stock > 0 else "out of stock",
            "price": f"{product.price} MXN",
            "image_link": product.images[0] if product.images else "",
            "google_product_category": product.category,
        }

    def external_order_id(self, payload: dict) -> str:
        return str(payload["id"])

    def to_canonical_order(self, payload: dict, canonical_id: str) -> CanonicalOrder:
        lines = [
            CanonicalOrderLine(
                sku=li.get("sku") or "-",
                name=li.get("name", ""),
                unit_price=float(li.get("unit_price", 0)),
                quantity=int(li.get("quantity", 1)),
            )
            for li in payload.get("items", [])
        ]
        return CanonicalOrder(
            canonical_id=canonical_id,
            channel=self.name,
            external_id=str(payload["id"]),
            status=payload.get("status", "pending"),
            lines=lines,
            total=float(payload.get("total", 0)),
            currency=payload.get("currency", "MXN"),
            customer_email=payload.get("email"),
        )
