"""Conector de Shopify (Admin API). Sprint 2.

Capacidades: catálogo, inventario, pedidos, fulfillment. Webhook `orders/create`
firmado con HMAC-SHA256 (header X-Shopify-Hmac-Sha256). Credenciales en el vault.
"""

from __future__ import annotations

from backend.integrations.canonical import CanonicalOrder, CanonicalOrderLine
from backend.integrations.connector import Capability
from backend.integrations.connectors.channel_base import ChannelConnector


class ShopifyConnector(ChannelConnector):
    name = "shopify"
    capabilities = {
        Capability.CATALOG,
        Capability.INVENTORY,
        Capability.ORDERS,
        Capability.FULFILLMENT,
    }
    webhook_signature_header = "X-Shopify-Hmac-Sha256"

    def external_order_id(self, payload: dict) -> str:
        return str(payload["id"])

    def to_canonical_order(self, payload: dict, canonical_id: str) -> CanonicalOrder:
        lines = [
            CanonicalOrderLine(
                sku=li.get("sku") or "-",
                name=li.get("title", ""),
                unit_price=float(li.get("price", 0)),
                quantity=int(li.get("quantity", 1)),
            )
            for li in payload.get("line_items", [])
        ]
        return CanonicalOrder(
            canonical_id=canonical_id,
            channel=self.name,
            external_id=str(payload["id"]),
            status=payload.get("financial_status", "pending"),
            lines=lines,
            total=float(payload.get("total_price", 0)),
            currency=payload.get("currency", "MXN"),
            customer_email=payload.get("email"),
        )
