"""Pruebas unitarias puras (sin DynamoDB): pricing, security, serde, OpenAPI."""

from __future__ import annotations

from decimal import Decimal

from backend.db.serde import from_item, to_item
from backend.pricing import compute_totals
from backend.schemas.store import StoreConfig
from backend.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)

# ── pricing ───────────────────────────────────────────────────────────────────


def test_pricing_basico():
    t = compute_totals(
        1000.0,
        StoreConfig(tax_rate=0.16, shipping_flat=99.0, free_shipping_threshold=None),
    )
    assert t["tax"] == 160.0
    assert t["shipping"] == 99.0
    assert t["total"] == 1259.0
    assert t["currency"] == "MXN"


def test_pricing_envio_gratis_por_umbral():
    t = compute_totals(
        2000.0,
        StoreConfig(tax_rate=0.16, shipping_flat=99.0, free_shipping_threshold=1500.0),
    )
    assert t["shipping"] == 0.0


def test_pricing_subtotal_cero_sin_envio():
    t = compute_totals(0.0, StoreConfig())
    assert t["shipping"] == 0.0 and t["total"] == 0.0


# ── security ──────────────────────────────────────────────────────────────────


def test_hash_verify_password():
    h = hash_password("secret123")
    assert verify_password("secret123", h)
    assert not verify_password("incorrecta", h)


def test_password_truncado_72_bytes():
    # bcrypt trunca a 72 bytes: passwords con los mismos 72 bytes iniciales coinciden.
    base = "a" * 72
    h = hash_password(base + "EXTRA-IGNORADO")
    assert verify_password(base, h)


def test_jwt_access_y_refresh():
    at = create_access_token({"sub": "u1"})
    rt = create_refresh_token({"sub": "u1"})
    pa = decode_token(at)
    pr = decode_token(rt)
    assert pa["sub"] == "u1" and pa["type"] == "access"
    assert pr["type"] == "refresh"
    assert decode_token("token-basura") is None


# ── serde DynamoDB ────────────────────────────────────────────────────────────


def test_to_item_float_a_decimal():
    item = to_item({"price": 10.5, "qty": 3, "name": "x"})
    assert isinstance(item["price"], Decimal)
    assert item["qty"] == 3


def test_from_item_decimal_a_numero():
    assert from_item({"price": Decimal("10.5"), "qty": Decimal("3")}) == {
        "price": 10.5,
        "qty": 3,
    }
    assert from_item(None) is None


def test_serde_anidado():
    out = from_item(to_item({"variants": [{"stock": 5, "price_delta": 1.5}]}))
    assert out["variants"][0]["stock"] == 5
    assert out["variants"][0]["price_delta"] == 1.5


# ── OpenAPI / Swagger ─────────────────────────────────────────────────────────


def test_openapi_schema_tags_y_paths():
    from backend.app import app

    schema = app.openapi()
    assert schema["info"]["title"] == "JV Market API"
    tags = {t["name"] for t in schema.get("tags", [])}
    assert {"auth", "products", "cart", "orders", "admin", "config"} <= tags
    paths = schema["paths"]
    for p in (
        "/api/products",
        "/api/auth/login",
        "/api/admin/dashboard",
        "/api/config",
    ):
        assert p in paths
    # Docs nativos deshabilitados: se sirven por rutas propias protegidas (ver candado).
    assert app.docs_url is None
    assert app.openapi_url is None


def test_docs_auth_check():
    """La verificación Basic de docs acepta credenciales correctas y rechaza malas."""
    import pytest
    from fastapi import HTTPException
    from fastapi.security import HTTPBasicCredentials

    from backend import app as appmod
    from backend.config import settings

    settings.DOCS_USER = "jvmarket"
    settings.DOCS_PASSWORD = "s3cret"
    ok = HTTPBasicCredentials(username="jvmarket", password="s3cret")
    assert appmod._check_docs_auth(ok) == "jvmarket"
    for bad in (
        HTTPBasicCredentials(username="x", password="s3cret"),
        HTTPBasicCredentials(username="jvmarket", password="mala"),
    ):
        with pytest.raises(HTTPException) as exc:
            appmod._check_docs_auth(bad)
        assert exc.value.status_code == 401


def test_docs_deshabilitados_sin_password(client):
    """Sin DOCS_PASSWORD configurada al importar la app, los docs responden 404."""
    assert client.get("/api/docs").status_code == 404
    assert client.get("/api/openapi.json").status_code == 404
