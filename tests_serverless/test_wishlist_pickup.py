"""Tests de v2: lista de deseos y click & collect (recoger en tienda)."""

from __future__ import annotations


def _cliente(client, email="comprador@shop.mx"):
    client.post(
        "/api/auth/register",
        json={"email": email, "password": "secret123", "full_name": "Comprador"},
    )
    r = client.post("/api/auth/login", json={"email": email, "password": "secret123"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def _producto(client, admin_headers, **over):
    payload = {
        "name": "Tenis Runner",
        "price": 1000.0,
        "category": "tenis",
        "variants": [{"sku": "RUN-42", "attrs": {"talla": "42"}, "stock": 5}],
    }
    payload.update(over)
    return client.post("/api/products", json=payload, headers=admin_headers).json()


# ── Wishlist ──────────────────────────────────────────────────────────────────


def test_wishlist_agregar_listar_quitar(client, admin_headers):
    prod = _producto(client, admin_headers)
    h = _cliente(client)

    assert client.get("/api/wishlist", headers=h).json() == []
    assert client.post(f"/api/wishlist/{prod['id']}", headers=h).status_code == 204

    wl = client.get("/api/wishlist", headers=h).json()
    assert len(wl) == 1 and wl[0]["id"] == prod["id"]

    # Idempotente: agregar de nuevo no duplica
    client.post(f"/api/wishlist/{prod['id']}", headers=h)
    assert len(client.get("/api/wishlist", headers=h).json()) == 1

    assert client.delete(f"/api/wishlist/{prod['id']}", headers=h).status_code == 204
    assert client.get("/api/wishlist", headers=h).json() == []


def test_wishlist_requiere_auth(client):
    assert client.get("/api/wishlist").status_code in (401, 403)


# ── Click & collect ───────────────────────────────────────────────────────────


def test_config_expone_pickup(client):
    cfg = client.get("/api/config").json()
    assert cfg["pickup_enabled"] is True
    assert any(loc["id"] == "cdmx-centro" for loc in cfg["pickup_locations"])


def test_checkout_pickup_sin_envio(client, admin_headers):
    prod = _producto(client, admin_headers)
    h = _cliente(client)
    client.post(
        "/api/cart/items",
        json={"product_id": prod["id"], "sku": "RUN-42", "quantity": 1},
        headers=h,
    )
    r = client.post(
        "/api/orders/checkout",
        json={"fulfillment": "pickup", "pickup_location_id": "cdmx-centro"},
        headers=h,
    )
    assert r.status_code == 201
    order = r.json()
    assert order["fulfillment"] == "pickup"
    assert order["shipping"] == 0.0
    assert order["pickup_location"]["id"] == "cdmx-centro"
    assert order["total"] == round(order["subtotal"] + order["tax"], 2)


def test_checkout_pickup_ubicacion_invalida(client, admin_headers):
    prod = _producto(client, admin_headers)
    h = _cliente(client)
    client.post(
        "/api/cart/items",
        json={"product_id": prod["id"], "sku": "RUN-42", "quantity": 1},
        headers=h,
    )
    r = client.post(
        "/api/orders/checkout",
        json={"fulfillment": "pickup", "pickup_location_id": "no-existe"},
        headers=h,
    )
    assert r.status_code == 422


def test_checkout_envio_normal_cobra_shipping(client, admin_headers):
    prod = _producto(client, admin_headers)
    h = _cliente(client)
    client.post(
        "/api/cart/items",
        json={"product_id": prod["id"], "sku": "RUN-42", "quantity": 1},
        headers=h,
    )
    r = client.post("/api/orders/checkout", json={"fulfillment": "ship"}, headers=h)
    assert r.status_code == 201
    order = r.json()
    assert order["fulfillment"] == "ship"
    assert order["shipping"] == 99.0
