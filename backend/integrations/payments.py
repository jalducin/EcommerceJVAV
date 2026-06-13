"""Conciliación de pagos: vincula un cobro del proveedor a un pedido canónico.

Idempotente: un transaction_id del proveedor -> un único Pago canónico (reenvíos de
webhook no duplican). PK = PAYMENT#<canonical_id>, SK = PAYMENT.
"""

from __future__ import annotations

import uuid

from backend.db.dynamo import get_table
from backend.db.serde import from_item, to_item
from backend.integrations import mapping
from backend.integrations.canonical import CanonicalPayment, EntityType
from backend.integrations.connectors.payment_base import PaymentConnector


def _pk(canonical_id: str) -> str:
    return f"PAYMENT#{canonical_id}"


def _save(payment: CanonicalPayment) -> None:
    item = to_item(payment.model_dump())
    item.update({"PK": _pk(payment.canonical_id), "SK": "PAYMENT", "entity": "payment"})
    get_table().put_item(Item=item)


def get_payment(canonical_id: str) -> CanonicalPayment | None:
    resp = get_table().get_item(Key={"PK": _pk(canonical_id), "SK": "PAYMENT"})
    item = from_item(resp.get("Item"))
    if not item:
        return None
    internal = ("PK", "SK", "entity")
    return CanonicalPayment(**{k: v for k, v in item.items() if k not in internal})


def reconcile(
    connector: PaymentConnector, payload: dict, order_id: str
) -> CanonicalPayment:
    """Concilia el cobro con el pedido. Idempotente por transaction_id."""
    tx_id = connector.external_payment_id(payload)
    existing_id = mapping.get_canonical_id(connector.name, EntityType.PAYMENT, tx_id)
    if existing_id:
        payment = get_payment(existing_id)
        if payment:
            return payment  # ya conciliado: no duplica

    canonical_id = str(uuid.uuid4())
    payment = connector.to_payment(payload, canonical_id, order_id)
    _save(payment)
    mapping.set_mapping(connector.name, EntityType.PAYMENT, tx_id, canonical_id)
    return payment
