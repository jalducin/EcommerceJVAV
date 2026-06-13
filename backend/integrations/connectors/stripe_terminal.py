"""Conector de Stripe Terminal (pagos presenciales). Sprint 6 — test mode."""

from __future__ import annotations

from backend.integrations.canonical import CanonicalPayment
from backend.integrations.connectors.payment_base import PaymentConnector


class StripeTerminalConnector(PaymentConnector):
    name = "stripe_terminal"

    def external_payment_id(self, payload: dict) -> str:
        return str(payload["id"])  # PaymentIntent id (pi_...)

    def to_payment(
        self, payload: dict, canonical_id: str, order_id: str
    ) -> CanonicalPayment:
        status = (
            "paid"
            if payload.get("status") == "succeeded"
            else payload.get("status", "pending")
        )
        return CanonicalPayment(
            canonical_id=canonical_id,
            order_id=order_id,
            provider=self.name,
            transaction_id=str(payload["id"]),
            amount=float(payload.get("amount", 0)) / 100.0,  # Stripe usa centavos
            currency=str(payload.get("currency", "mxn")).upper(),
            status=status,
        )
