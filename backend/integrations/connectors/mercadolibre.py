"""Conector de MercadoLibre (LATAM). Sprint 3 — ejecutable con test users.

Auth OAuth 2.0 (token en el vault). Los pedidos llegan por notificaciones (topics):
se valida la forma de la notificación y luego se ingiere el pedido obtenido por la
Orders API. Capacidades: catálogo, inventario, pedidos.
"""

from __future__ import annotations

from backend.integrations.canonical import CanonicalOrder, CanonicalOrderLine
from backend.integrations.connector import Capability
from backend.integrations.connectors.channel_base import ChannelConnector


class MercadoLibreConnector(ChannelConnector):
    name = "mercadolibre"
    capabilities = {Capability.CATALOG, Capability.INVENTORY, Capability.ORDERS}

    def verify_webhook(
        self, secret: str, raw_body: bytes, signature: str | None
    ) -> bool:
        # MercadoLibre no firma con HMAC; la autenticidad se confirma al obtener el
        # recurso con el token. Aquí validamos la forma de la notificación.
        import json

        try:
            data = json.loads(raw_body.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return False
        return bool(data.get("topic")) and bool(data.get("resource"))

    def external_order_id(self, payload: dict) -> str:
        return str(payload["id"])

    def to_canonical_order(self, payload: dict, canonical_id: str) -> CanonicalOrder:
        lines = [
            CanonicalOrderLine(
                sku=(it.get("item") or {}).get("seller_sku")
                or (it.get("item") or {}).get("seller_custom_field")
                or "-",
                name=(it.get("item") or {}).get("title", ""),
                unit_price=float(it.get("unit_price", 0)),
                quantity=int(it.get("quantity", 1)),
            )
            for it in payload.get("order_items", [])
        ]
        buyer = payload.get("buyer") or {}
        return CanonicalOrder(
            canonical_id=canonical_id,
            channel=self.name,
            external_id=str(payload["id"]),
            status=payload.get("status", "pending"),
            lines=lines,
            total=float(payload.get("total_amount", 0)),
            currency=payload.get("currency_id", "MXN"),
            customer_email=buyer.get("email"),
        )
