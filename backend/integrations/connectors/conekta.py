"""Conector de Conekta (pagos, México). Sprint 6 — ejecutable en sandbox."""

from __future__ import annotations

from backend.integrations.canonical import CanonicalPayment
from backend.integrations.connectors.payment_base import PaymentConnector


class ConektaConnector(PaymentConnector):
    name = "conekta"

    def external_payment_id(self, payload: dict) -> str:
        return str(payload["id"])

    def to_payment(
        self, payload: dict, canonical_id: str, order_id: str
    ) -> CanonicalPayment:
        status = (
            "paid"
            if payload.get("status") == "paid"
            else payload.get("status", "pending")
        )
        return CanonicalPayment(
            canonical_id=canonical_id,
            order_id=order_id,
            provider=self.name,
            transaction_id=str(payload["id"]),
            amount=float(payload.get("amount", 0)) / 100.0,  # Conekta usa centavos
            currency=str(payload.get("currency", "MXN")).upper(),
            status=status,
        )
