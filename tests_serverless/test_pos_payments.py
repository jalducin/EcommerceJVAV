"""Tests de Sprint 6: POS (Square/Lightspeed) y pagos (Stripe Terminal/Clip/Conekta)."""

from __future__ import annotations

from backend.integrations.connector import Capability
from backend.integrations.connectors.clip import ClipConnector
from backend.integrations.connectors.conekta import ConektaConnector
from backend.integrations.connectors.lightspeed import LightspeedConnector
from backend.integrations.connectors.square import SquareConnector
from backend.integrations.connectors.stripe_terminal import StripeTerminalConnector


def _seed(dynamo):
    from backend.repositories import product_repo
    from backend.schemas.catalog import ProductCreate, Variant

    product_repo.create_product(
        ProductCreate(
            name="Tenis Runner",
            price=1000.0,
            category="tenis",
            variants=[Variant(sku="RUN-42", attrs={"talla": "42"}, stock=10)],
        )
    )


# ── Capacidades / deuda técnica ───────────────────────────────────────────────


def test_capacidades_pos_pagos():
    sq = SquareConnector()
    assert sq.supports(Capability.ORDERS) and sq.supports(Capability.PAYMENTS)
    for pay in (StripeTerminalConnector(), ClipConnector(), ConektaConnector()):
        assert pay.supports(Capability.PAYMENTS)
        assert not pay.supports(Capability.ORDERS)
    assert LightspeedConnector().deferred is True


# ── POS Square: venta presencial al hub + inventario ──────────────────────────


def test_square_pos_ingesta_y_inventario(dynamo):
    from backend.integrations import channel_orders, ingest, inventory

    _seed(dynamo)
    payload = {
        "id": "sq-order-1",
        "state": "COMPLETED",
        "total_money": {"amount": 200000, "currency": "MXN"},
        "line_items": [
            {
                "sku": "RUN-42",
                "name": "Tenis",
                "base_price_money": {"amount": 100000},
                "quantity": 2,
            }
        ],
    }
    order = ingest.ingest_order(SquareConnector(), payload)
    assert order.channel == "square"
    assert order.lines[0].unit_price == 1000.0  # 100000 centavos / 100
    assert len(channel_orders.list_orders(channel="square")) == 1
    pid = inventory.find_product_id_by_sku("RUN-42")
    assert inventory.get_stock(pid, "RUN-42") == 8


# ── Pagos: conciliación idempotente vinculada al pedido ───────────────────────


def test_stripe_terminal_concilia_idempotente(dynamo):
    from backend.integrations import payments

    conn = StripeTerminalConnector()
    pi = {"id": "pi_123", "status": "succeeded", "amount": 200000, "currency": "mxn"}
    p1 = payments.reconcile(conn, pi, order_id="ord-1")
    p2 = payments.reconcile(conn, pi, order_id="ord-1")  # reenvío de webhook

    assert p1.canonical_id == p2.canonical_id  # no duplica
    assert p1.status == "paid"
    assert p1.amount == 2000.0  # centavos -> pesos
    assert p1.currency == "MXN"
    assert p1.order_id == "ord-1"
    assert payments.get_payment(p1.canonical_id) is not None


def test_conekta_y_clip_mapeo(dynamo):
    from backend.integrations import payments

    conekta = payments.reconcile(
        ConektaConnector(),
        {"id": "chrg_1", "status": "paid", "amount": 150000, "currency": "MXN"},
        order_id="ord-2",
    )
    assert conekta.amount == 1500.0 and conekta.status == "paid"

    clip = payments.reconcile(
        ClipConnector(),
        {"id": "clip_1", "status": "approved", "amount": 999.0, "currency": "MXN"},
        order_id="ord-3",
    )
    assert clip.amount == 999.0 and clip.status == "paid"


def test_payment_webhook_hmac():
    conn = ConektaConnector()
    from backend.integrations.webhooks import hmac_sha256_base64

    body = b'{"id":"chrg_1"}'
    firma = hmac_sha256_base64("wh_secret", body)
    assert conn.verify_webhook("wh_secret", body, firma) is True
    assert conn.verify_webhook("wh_secret", body, "mala") is False
