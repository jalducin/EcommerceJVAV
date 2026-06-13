"""Tests de Sprint 4: Meta, TikTok Shop y Google Merchant (feed)."""

from __future__ import annotations

from backend.integrations.connector import Capability
from backend.integrations.connectors.google_merchant import GoogleMerchantConnector
from backend.integrations.connectors.meta import MetaConnector
from backend.integrations.connectors.tiktok import TikTokShopConnector
from backend.integrations.webhooks import hmac_sha256_hex


def _seed(dynamo, images=None):
    from backend.repositories import product_repo
    from backend.schemas.catalog import ProductCreate, Variant

    return product_repo.create_product(
        ProductCreate(
            name="Tenis Runner",
            price=1000.0,
            category="tenis",
            images=["https://img/x.jpg"] if images is None else images,
            variants=[Variant(sku="RUN-42", attrs={"talla": "42"}, stock=10)],
        )
    )


def test_meta_verify_webhook_hex_prefijo():
    conn = MetaConnector()
    secret = "meta_app_secret"
    body = b'{"entry":[]}'
    firma = "sha256=" + hmac_sha256_hex(secret, body)
    assert conn.verify_webhook(secret, body, firma) is True
    assert (
        conn.verify_webhook(secret, body, hmac_sha256_hex(secret, body)) is False
    )  # sin prefijo
    assert conn.verify_webhook(secret, body, None) is False


def test_tiktok_ingesta_idempotente(dynamo):
    from backend.integrations import channel_orders, ingest, inventory

    _seed(dynamo)
    conn = TikTokShopConnector()
    payload = {
        "order_id": "TT-777",
        "order_status": "AWAITING_SHIPMENT",
        "payment_total": 2000,
        "currency": "MXN",
        "buyer_email": "tiktok@correo.mx",
        "order_line_items": [
            {
                "seller_sku": "RUN-42",
                "product_name": "Tenis",
                "sale_price": 1000,
                "quantity": 2,
            }
        ],
    }
    o1 = ingest.ingest_order(conn, payload)
    o2 = ingest.ingest_order(conn, payload)
    assert o1.canonical_id == o2.canonical_id
    assert o1.channel == "tiktok"
    assert len(channel_orders.list_orders(channel="tiktok")) == 1
    pid = inventory.find_product_id_by_sku("RUN-42")
    assert inventory.get_stock(pid, "RUN-42") == 8


def test_google_merchant_solo_feed_sin_pedidos():
    conn = GoogleMerchantConnector()
    assert conn.supports(Capability.CATALOG)
    assert not conn.supports(Capability.ORDERS)


def test_build_feed_reporta_invalidos_sin_abortar(dynamo):
    from backend.integrations.feeds import build_feed

    ok = _seed(dynamo)  # con imagen
    sin_img = _seed(dynamo, images=[])  # sin imagen -> rechazado por Google

    result = build_feed(GoogleMerchantConnector(), [ok, sin_img])
    assert result["count"] == 1
    assert result["rejected"] == 1
    assert result["errors"][0]["product_id"] == sin_img.id
    assert result["items"][0]["offerId"] == ok.id


def test_meta_feed_item(dynamo):
    from backend.integrations.feeds import build_feed

    prod = _seed(dynamo)
    result = build_feed(MetaConnector(), [prod])
    assert result["count"] == 1
    item = result["items"][0]
    assert item["title"] == "Tenis Runner"
    assert item["availability"] == "in stock"
