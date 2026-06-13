"""Base de conectores de canal de venta (e-commerce, marketplace, social).

Define el contrato que usa la ingesta de pedidos: verificación de webhook,
identificación del pedido externo y traducción al modelo canónico.
"""

from __future__ import annotations

from abc import abstractmethod

from backend.integrations.canonical import CanonicalOrder
from backend.integrations.connector import ConnectorBase
from backend.integrations.webhooks import verify_hmac


class ChannelConnector(ConnectorBase):
    # Header donde el proveedor envía la firma HMAC del webbook.
    webhook_signature_header: str = ""

    def verify_webhook(
        self, secret: str, raw_body: bytes, signature: str | None
    ) -> bool:
        return verify_hmac(secret, raw_body, signature)

    @abstractmethod
    def external_order_id(self, payload: dict) -> str: ...

    @abstractmethod
    def to_canonical_order(
        self, payload: dict, canonical_id: str
    ) -> CanonicalOrder: ...
