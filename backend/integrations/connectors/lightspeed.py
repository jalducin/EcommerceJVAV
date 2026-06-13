"""Conector de Lightspeed (POS retail). Sprint 6 — DEUDA TECNICA (diferido).

Requiere cuenta retail de pago; no ejecutable en tier 0. El mapeo de venta a pedido
canonico se prueba; la verificacion en vivo queda diferida.
"""

from __future__ import annotations

from backend.integrations.canonical import CanonicalOrder, CanonicalOrderLine
from backend.integrations.connector import Capability
from backend.integrations.connectors.channel_base import ChannelConnector


class LightspeedConnector(ChannelConnector):
    name = "lightspeed"
    capabilities = {Capability.CATALOG, Capability.INVENTORY, Capability.ORDERS}
    deferred = True

    def external_order_id(self, payload: dict) -> str:
        return str(payload["saleID"])

    def to_canonical_order(self, payload: dict, canonical_id: str) -> CanonicalOrder:
        lines = [
            CanonicalOrderLine(
                sku=li.get("sku") or "-",
                name=li.get("description", ""),
                unit_price=float(li.get("unitPrice", 0)),
                quantity=int(li.get("unitQuantity", 1)),
            )
            for li in payload.get("SaleLines", [])
        ]
        return CanonicalOrder(
            canonical_id=canonical_id,
            channel=self.name,
            external_id=str(payload["saleID"]),
            status=payload.get("completed", "pending"),
            lines=lines,
            total=float(payload.get("total", 0)),
            currency="MXN",
        )
