"""Conector de Square (POS retail + pagos). Sprint 6 — ejecutable en sandbox.

POS: las ventas presenciales entran al hub de pedidos y descuentan inventario. Tambien
soporta pagos. Capacidades: catalogo, inventario, pedidos, pagos.
"""

from __future__ import annotations

from backend.integrations.canonical import CanonicalOrder, CanonicalOrderLine
from backend.integrations.connector import Capability
from backend.integrations.connectors.channel_base import ChannelConnector


class SquareConnector(ChannelConnector):
    name = "square"
    capabilities = {
        Capability.CATALOG,
        Capability.INVENTORY,
        Capability.ORDERS,
        Capability.PAYMENTS,
    }
    webhook_signature_header = "x-square-hmacsha256-signature"

    def external_order_id(self, payload: dict) -> str:
        return str(payload["id"])

    def to_canonical_order(self, payload: dict, canonical_id: str) -> CanonicalOrder:
        lines = [
            CanonicalOrderLine(
                sku=li.get("sku") or li.get("catalog_object_id") or "-",
                name=li.get("name", ""),
                unit_price=float((li.get("base_price_money") or {}).get("amount", 0))
                / 100.0,
                quantity=int(li.get("quantity", 1)),
            )
            for li in payload.get("line_items", [])
        ]
        total = payload.get("total_money") or {}
        return CanonicalOrder(
            canonical_id=canonical_id,
            channel=self.name,
            external_id=str(payload["id"]),
            status=payload.get("state", "pending"),
            lines=lines,
            total=float(total.get("amount", 0)) / 100.0,
            currency=str(total.get("currency", "MXN")).upper(),
        )
