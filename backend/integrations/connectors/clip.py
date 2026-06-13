"""Conector de Clip (pagos presenciales, México). Sprint 6 — ejecutable en sandbox."""

from __future__ import annotations

from backend.integrations.canonical import CanonicalPayment
from backend.integrations.connectors.payment_base import PaymentConnector


class ClipConnector(PaymentConnector):
    name = "clip"

    def external_payment_id(self, payload: dict) -> str:
        return str(payload["id"])

    def to_payment(
        self, payload: dict, canonical_id: str, order_id: str
    ) -> CanonicalPayment:
        status = (
            "paid"
            if payload.get("status") in ("approved", "paid")
            else payload.get("status", "pending")
        )
        return CanonicalPayment(
            canonical_id=canonical_id,
            order_id=order_id,
            provider=self.name,
            transaction_id=str(payload["id"]),
            amount=float(payload.get("amount", 0)),
            currency=str(payload.get("currency", "MXN")).upper(),
            status=status,
        )
