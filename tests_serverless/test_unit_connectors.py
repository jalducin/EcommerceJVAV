"""Pruebas unitarias de mapeo de conectores (funciones puras, sin DynamoDB)."""

from __future__ import annotations

from backend.integrations.canonical import CanonicalCustomer
from backend.integrations.connectors.conekta import ConektaConnector
from backend.integrations.connectors.google_merchant import GoogleMerchantConnector
from backend.integrations.connectors.hubspot import HubSpotConnector
from backend.integrations.connectors.mercadolibre import MercadoLibreConnector
from backend.integrations.connectors.shopify import ShopifyConnector
from backend.integrations.connectors.square import SquareConnector
from backend.integrations.connectors.stripe_terminal import StripeTerminalConnector
from backend.integrations.feeds import FeedItemError
from backend.schemas.catalog import Product, Variant


def _producto(**over):
    base = dict(
        id="p1",
        name="Tenis",
        price=1000.0,
        category="tenis",
        images=["https://img/x.jpg"],
        created_at="2026-01-01T00:00:00+00:00",
        variants=[Variant(sku="RUN-42", attrs={"talla": "42"}, stock=3)],
    )
    base.update(over)
    return Product(**base)


def test_shopify_to_canonical_order():
    o = ShopifyConnector().to_canonical_order(
        {
            "id": 9,
            "financial_status": "paid",
            "total_price": "2000",
            "currency": "MXN",
            "line_items": [
                {"sku": "RUN-42", "title": "T", "price": "1000", "quantity": 2}
            ],
        },
        "c1",
    )
    assert o.channel == "shopify" and o.external_id == "9"
    assert o.lines[0].sku == "RUN-42" and o.lines[0].quantity == 2


def test_mercadolibre_seller_sku():
    o = MercadoLibreConnector().to_canonical_order(
        {
            "id": 5,
            "status": "paid",
            "total_amount": 1000,
            "currency_id": "MXN",
            "order_items": [
                {"item": {"seller_sku": "RUN-42"}, "quantity": 1, "unit_price": 1000}
            ],
        },
        "c2",
    )
    assert o.lines[0].sku == "RUN-42"


def test_square_centavos_a_pesos():
    o = SquareConnector().to_canonical_order(
        {
            "id": "sq1",
            "state": "COMPLETED",
            "total_money": {"amount": 200000, "currency": "MXN"},
            "line_items": [
                {"sku": "RUN-42", "base_price_money": {"amount": 100000}, "quantity": 2}
            ],
        },
        "c3",
    )
    assert o.total == 2000.0 and o.lines[0].unit_price == 1000.0


def test_stripe_y_conekta_to_payment():
    sp = StripeTerminalConnector().to_payment(
        {"id": "pi_1", "status": "succeeded", "amount": 200000, "currency": "mxn"},
        "p1",
        "ord-1",
    )
    assert sp.amount == 2000.0 and sp.status == "paid" and sp.currency == "MXN"
    ck = ConektaConnector().to_payment(
        {"id": "ch_1", "status": "paid", "amount": 150000, "currency": "MXN"},
        "p2",
        "ord-2",
    )
    assert ck.amount == 1500.0 and ck.order_id == "ord-2"


def test_hubspot_to_contact():
    c = HubSpotConnector().to_contact(
        CanonicalCustomer(canonical_id="x", email="ana@correo.mx", full_name="Ana")
    )
    assert c == {"email": "ana@correo.mx", "name": "Ana"}


def test_google_feed_item_y_rechazo_sin_imagen():
    gm = GoogleMerchantConnector()
    item = gm.to_feed_item(_producto())
    assert item["offerId"] == "p1"
    assert item["availability"] == "in stock"
    try:
        gm.to_feed_item(_producto(images=[]))
        assert False, "debió rechazar producto sin imagen"
    except FeedItemError:
        pass
