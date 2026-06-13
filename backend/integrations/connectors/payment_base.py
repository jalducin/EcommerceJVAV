"""Base de conectores de pago presencial (POS / pasarelas).

Capacidad PAYMENTS. `to_payment` mapea el payload del proveedor a un Pago canónico;
la conciliación (idempotente, un transaction_id -> un Pago) vive en `payments`.
Por defecto la firma del webhook se valida con HMAC-SHA256 base64.
"""

from __future__ import annotations

from abc import abstractmethod

from backend.integrations.canonical import CanonicalPayment
from backend.integrations.connector import Capability, ConnectorBase
from backend.integrations.webhooks import verify_hmac


class PaymentConnector(ConnectorBase):
    capabilities = {Capability.PAYMENTS}

    def verify_webhook(
        self, secret: str, raw_body: bytes, signature: str | None
    ) -> bool:
        return verify_hmac(secret, raw_body, signature)

    @abstractmethod
    def external_payment_id(self, payload: dict) -> str: ...

    @abstractmethod
    def to_payment(
        self, payload: dict, canonical_id: str, order_id: str
    ) -> CanonicalPayment: ...
