"""Conector de Amazon SP-API. Sprint 3 — DEUDA TÉCNICA (diferido).

Specced y codificado, pero NO ejecutable en tier 0: requiere cuenta de vendedor
profesional + aprobación de la app (LWA/OAuth). `deferred = True`; su verificación en
vivo queda pendiente de acceso. El mapeo a canónico sí se prueba con payloads grabados.
"""

from __future__ import annotations

from backend.integrations.canonical import CanonicalOrder, CanonicalOrderLine
from backend.integrations.connector import Capability
from backend.integrations.connectors.channel_base import ChannelConnector


class AmazonConnector(ChannelConnector):
    name = "amazon"
    capabilities = {Capability.CATALOG, Capability.INVENTORY, Capability.ORDERS}
    deferred = True  # requiere cuenta de vendedor + aprobación (no tier 0)

    def external_order_id(self, payload: dict) -> str:
        return str(payload["AmazonOrderId"])

    def to_canonical_order(self, payload: dict, canonical_id: str) -> CanonicalOrder:
        lines = [
            CanonicalOrderLine(
                sku=it.get("SellerSKU") or "-",
                name=it.get("Title", ""),
                unit_price=float((it.get("ItemPrice") or {}).get("Amount", 0)),
                quantity=int(it.get("QuantityOrdered", 1)),
            )
            for it in payload.get("items", [])
        ]
        total = payload.get("OrderTotal") or {}
        buyer = payload.get("BuyerInfo") or {}
        return CanonicalOrder(
            canonical_id=canonical_id,
            channel=self.name,
            external_id=str(payload["AmazonOrderId"]),
            status=payload.get("OrderStatus", "pending"),
            lines=lines,
            total=float(total.get("Amount", 0)),
            currency=total.get("CurrencyCode", "MXN"),
            customer_email=buyer.get("BuyerEmail"),
        )
