"""Tests de Sprint 3: marketplaces (MercadoLibre ejecutable, Amazon diferido)."""

from __future__ import annotations

from backend.integrations.connectors.amazon import AmazonConnector
from backend.integrations.connectors.mercadolibre import MercadoLibreConnector


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


def _meli_order(order_id=300):
    return {
        "id": order_id,
        "status": "paid",
        "total_amount": 2000,
        "currency_id": "MXN",
        "buyer": {"email": "comprador@meli.mx"},
        "order_items": [
            {
                "item": {"seller_sku": "RUN-42", "title": "Tenis"},
                "quantity": 2,
                "unit_price": 1000,
            }
        ],
    }


def test_meli_verify_webhook_shape():
    conn = MercadoLibreConnector()
    ok = b'{"topic":"orders_v2","resource":"/orders/123"}'
    assert conn.verify_webhook("", ok, None) is True
    assert conn.verify_webhook("", b'{"foo":"bar"}', None) is False
    assert conn.verify_webhook("", b"no-json", None) is False


def test_meli_ingesta_idempotente_y_inventario(dynamo):
    from backend.integrations import channel_orders, ingest, inventory

    _seed(dynamo)
    conn = MercadoLibreConnector()
    o1 = ingest.ingest_order(conn, _meli_order(order_id=301))
    o2 = ingest.ingest_order(conn, _meli_order(order_id=301))

    assert o1.canonical_id == o2.canonical_id
    assert o1.channel == "mercadolibre"
    assert o1.lines[0].sku == "RUN-42"
    assert len(channel_orders.list_orders(channel="mercadolibre")) == 1
    pid = inventory.find_product_id_by_sku("RUN-42")
    assert inventory.get_stock(pid, "RUN-42") == 8  # 10 - 2, una sola vez


def test_amazon_marcado_deferido_y_mapeo(dynamo):
    from backend.integrations import ingest

    conn = AmazonConnector()
    assert conn.deferred is True  # deuda técnica

    # El mapeo a canónico sí se prueba (payload grabado), aunque no se ejecute en vivo.
    _seed(dynamo)
    payload = {
        "AmazonOrderId": "902-1234567-1234567",
        "OrderStatus": "Shipped",
        "OrderTotal": {"Amount": "1000.00", "CurrencyCode": "MXN"},
        "BuyerInfo": {"BuyerEmail": "x@marketplace.amazon.com"},
        "items": [
            {
                "SellerSKU": "RUN-42",
                "Title": "Tenis",
                "QuantityOrdered": 1,
                "ItemPrice": {"Amount": "1000"},
            }
        ],
    }
    order = ingest.ingest_order(conn, payload)
    assert order.channel == "amazon"
    assert order.external_id == "902-1234567-1234567"
    assert order.lines[0].quantity == 1
