"""Conector de WooCommerce (REST API). Sprint 2.

Capacidades: catálogo, inventario, pedidos, fulfillment. Webhook firmado con
HMAC-SHA256 (header X-WC-Webhook-Signature). Credenciales en el vault.
"""

from __future__ import annotations

from backend.integrations.canonical import CanonicalOrder, CanonicalOrderLine
from backend.integrations.connector import Capability
from backend.integrations.connectors.channel_base import ChannelConnector


class WooCommerceConnector(ChannelConnector):
    name = "woocommerce"
    capabilities = {
        Capability.CATALOG,
        Capability.INVENTORY,
        Capability.ORDERS,
        Capability.FULFILLMENT,
    }
    webhook_signature_header = "X-WC-Webhook-Signature"

    def external_order_id(self, payload: dict) -> str:
        return str(payload["id"])

    def to_canonical_order(self, payload: dict, canonical_id: str) -> CanonicalOrder:
        lines = [
            CanonicalOrderLine(
                sku=li.get("sku") or "-",
                name=li.get("name", ""),
                unit_price=float(li.get("price", 0)),
                quantity=int(li.get("quantity", 1)),
            )
            for li in payload.get("line_items", [])
        ]
        billing = payload.get("billing") or {}
        return CanonicalOrder(
            canonical_id=canonical_id,
            channel=self.name,
            external_id=str(payload["id"]),
            status=payload.get("status", "pending"),
            lines=lines,
            total=float(payload.get("total", 0)),
            currency=payload.get("currency", "MXN"),
            customer_email=billing.get("email"),
        )
