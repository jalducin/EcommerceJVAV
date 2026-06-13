"""Tests de Sprint 2: conectores Shopify/WooCommerce (webhooks, ingesta, inventario)."""

from __future__ import annotations

from backend.integrations.connectors.shopify import ShopifyConnector
from backend.integrations.connectors.woocommerce import WooCommerceConnector
from backend.integrations.webhooks import hmac_sha256_base64


def _seed_producto(dynamo):
    from backend.repositories import product_repo
    from backend.schemas.catalog import ProductCreate, Variant

    return product_repo.create_product(
        ProductCreate(
            name="Tenis Runner",
            price=1000.0,
            category="tenis",
            variants=[Variant(sku="RUN-42", attrs={"talla": "42"}, stock=10)],
        )
    )


def _shopify_payload(order_id=5001):
    return {
        "id": order_id,
        "financial_status": "paid",
        "total_price": "2000.00",
        "currency": "MXN",
        "email": "cliente@correo.mx",
        "line_items": [
            {
                "sku": "RUN-42",
                "title": "Tenis Runner",
                "price": "1000.00",
                "quantity": 2,
            }
        ],
    }


# ── Webhook HMAC ──────────────────────────────────────────────────────────────


def test_webhook_hmac_valido_e_invalido():
    conn = ShopifyConnector()
    secret = "shpss_test"
    body = b'{"id":1}'
    firma = hmac_sha256_base64(secret, body)
    assert conn.verify_webhook(secret, body, firma) is True
    assert conn.verify_webhook(secret, body, "firma-mala") is False
    assert conn.verify_webhook(secret, body, None) is False


# ── Capacidades ───────────────────────────────────────────────────────────────


def test_capacidades_declaradas():
    from backend.integrations.connector import Capability

    for conn in (ShopifyConnector(), WooCommerceConnector()):
        assert conn.supports(Capability.ORDERS)
        assert conn.supports(Capability.INVENTORY)
        assert not conn.supports(Capability.PAYMENTS)


# ── Ingesta idempotente + inventario ──────────────────────────────────────────


def test_ingesta_shopify_crea_pedido_y_refleja_inventario(dynamo):
    from backend.integrations import channel_orders, ingest, inventory

    _seed_producto(dynamo)
    conn = ShopifyConnector()
    order = ingest.ingest_order(conn, _shopify_payload())

    assert order.channel == "shopify"
    assert order.external_id == "5001"
    assert len(order.lines) == 1
    # Inventario reflejado: 10 - 2 = 8
    pid = inventory.find_product_id_by_sku("RUN-42")
    assert pid is not None
    assert inventory.get_stock(pid, "RUN-42") == 8
    # En el hub
    assert len(channel_orders.list_orders(channel="shopify")) == 1


def test_ingesta_idempotente_no_duplica(dynamo):
    from backend.integrations import channel_orders, ingest, inventory

    _seed_producto(dynamo)
    conn = ShopifyConnector()
    o1 = ingest.ingest_order(conn, _shopify_payload(order_id=7001))
    o2 = ingest.ingest_order(
        conn, _shopify_payload(order_id=7001)
    )  # mismo pedido externo

    assert o1.canonical_id == o2.canonical_id  # mismo canónico, no duplica
    assert len(channel_orders.list_orders()) == 1
    # El inventario solo se descontó una vez (10 - 2 = 8)
    pid = inventory.find_product_id_by_sku("RUN-42")
    assert inventory.get_stock(pid, "RUN-42") == 8


def test_ingesta_woocommerce(dynamo):
    from backend.integrations import channel_orders, ingest

    _seed_producto(dynamo)
    conn = WooCommerceConnector()
    payload = {
        "id": 9100,
        "status": "processing",
        "total": "1000.00",
        "currency": "MXN",
        "billing": {"email": "woo@correo.mx"},
        "line_items": [
            {"sku": "RUN-42", "name": "Tenis Runner", "price": "1000.00", "quantity": 1}
        ],
    }
    order = ingest.ingest_order(conn, payload)
    assert order.channel == "woocommerce"
    assert order.customer_email == "woo@correo.mx"
    assert len(channel_orders.list_orders(channel="woocommerce")) == 1


def test_dos_canales_en_el_hub(dynamo):
    from backend.integrations import channel_orders, ingest

    _seed_producto(dynamo)
    ingest.ingest_order(ShopifyConnector(), _shopify_payload(order_id=1))
    ingest.ingest_order(
        WooCommerceConnector(),
        {
            "id": 2,
            "status": "processing",
            "total": "500",
            "currency": "MXN",
            "line_items": [
                {"sku": "RUN-42", "name": "x", "price": "500", "quantity": 1}
            ],
        },
    )
    todos = channel_orders.list_orders()
    canales = {o.channel for o in todos}
    assert canales == {"shopify", "woocommerce"}
    assert len(todos) == 2
