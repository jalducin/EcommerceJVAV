"""Tests del backend del panel admin (Sprint 7): dashboard, pedidos, conectores."""

from __future__ import annotations


def _admin_headers(client):
    from backend.repositories import user_repo
    from backend.schemas.account import UserCreate

    user_repo.create_user(
        UserCreate(email="admin@shop.mx", password="adminpass", full_name="Admin"),
        role="admin",
    )
    r = client.post(
        "/api/auth/login", json={"email": "admin@shop.mx", "password": "adminpass"}
    )
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def _cliente_headers(client, email="cli@shop.mx"):
    client.post(
        "/api/auth/register",
        json={"email": email, "password": "secret123", "full_name": "Cli"},
    )
    r = client.post("/api/auth/login", json={"email": email, "password": "secret123"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_dashboard_requiere_admin(client):
    # sin token
    assert client.get("/api/admin/dashboard").status_code in (401, 403)
    # cliente normal -> 403
    h = _cliente_headers(client)
    assert client.get("/api/admin/dashboard", headers=h).status_code == 403


def test_dashboard_metricas(client, admin_headers):
    # producto con stock bajo
    client.post(
        "/api/products",
        json={
            "name": "Gorra",
            "price": 100.0,
            "category": "ropa",
            "stock": 2,
            "variants": [],
        },
        headers=admin_headers,
    )
    data = client.get("/api/admin/dashboard", headers=admin_headers).json()
    assert "sales_total" in data
    assert data["low_stock_count"] >= 1
    assert data["connectors"]["total"] == 18
    assert (
        data["connectors"]["deferred"] >= 3
    )  # amazon, netsuite, salesforce, lightspeed


def test_connectors_view(client, admin_headers):
    conns = client.get("/api/admin/connectors", headers=admin_headers).json()
    names = {c["name"] for c in conns}
    assert {"shopify", "mercadolibre", "hubspot", "square", "conekta"} <= names
    amazon = next(c for c in conns if c["name"] == "amazon")
    assert amazon["deferred"] is True
    assert amazon["status"] == "deuda_tecnica"


def test_unified_orders_incluye_canales(client, admin_headers, dynamo):
    from backend.integrations import ingest
    from backend.integrations.connectors.shopify import ShopifyConnector

    # un pedido de canal
    client.post(
        "/api/products",
        json={
            "name": "T",
            "price": 1000.0,
            "category": "tenis",
            "variants": [{"sku": "RUN-42", "attrs": {"talla": "42"}, "stock": 5}],
        },
        headers=admin_headers,
    )
    ingest.ingest_order(
        ShopifyConnector(),
        {
            "id": 1,
            "financial_status": "paid",
            "total_price": "1000",
            "currency": "MXN",
            "line_items": [
                {"sku": "RUN-42", "title": "T", "price": "1000", "quantity": 1}
            ],
        },
    )
    orders = client.get("/api/admin/orders", headers=admin_headers).json()
    canales = {o["source"] for o in orders}
    assert "channel" in canales
    assert any(o["channel"] == "shopify" for o in orders)
