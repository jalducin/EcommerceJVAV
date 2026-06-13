"""Conector de TikTok Shop. Sprint 4.

Capacidades: catálogo, inventario y pedidos. Webhook firmado con HMAC-SHA256 (hex).
"""

from __future__ import annotations

from backend.integrations.canonical import CanonicalOrder, CanonicalOrderLine
from backend.integrations.connector import Capability
from backend.integrations.connectors.channel_base import ChannelConnector
from backend.integrations.webhooks import verify_hmac_hex


class TikTokShopConnector(ChannelConnector):
    name = "tiktok"
    capabilities = {Capability.CATALOG, Capability.INVENTORY, Capability.ORDERS}
    webhook_signature_header = "X-Tts-Signature"

    def verify_webhook(
        self, secret: str, raw_body: bytes, signature: str | None
    ) -> bool:
        return verify_hmac_hex(secret, raw_body, signature)

    def to_feed_item(self, product) -> dict:
        return {
            "sku_id": product.id,
            "title": product.name,
            "stock": product.total_stock,
            "price": product.price,
            "currency": "MXN",
            "image": product.images[0] if product.images else "",
        }

    def external_order_id(self, payload: dict) -> str:
        return str(payload["order_id"])

    def to_canonical_order(self, payload: dict, canonical_id: str) -> CanonicalOrder:
        lines = [
            CanonicalOrderLine(
                sku=li.get("seller_sku") or "-",
                name=li.get("product_name", ""),
                unit_price=float(li.get("sale_price", 0)),
                quantity=int(li.get("quantity", 1)),
            )
            for li in payload.get("order_line_items", [])
        ]
        return CanonicalOrder(
            canonical_id=canonical_id,
            channel=self.name,
            external_id=str(payload["order_id"]),
            status=payload.get("order_status", "pending"),
            lines=lines,
            total=float(payload.get("payment_total", 0)),
            currency=payload.get("currency", "MXN"),
            customer_email=payload.get("buyer_email"),
        )
