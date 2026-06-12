"""Tests de carrito y checkout transaccional (anti-sobreventa)."""

from __future__ import annotations


def _registrar_login(client, email="comprador@shop.mx"):
    client.post(
        "/api/auth/register",
        json={"email": email, "password": "secret123", "full_name": "Comprador"},
    )
    tokens = client.post(
        "/api/auth/login", json={"email": email, "password": "secret123"}
    ).json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def _crear_producto(client, admin_headers, **over):
    payload = {
        "name": "Tenis Runner",
        "price": 1000.0,
        "category": "tenis",
        "variants": [{"sku": "RUN-42", "attrs": {"talla": "42"}, "stock": 3}],
    }
    payload.update(over)
    return client.post("/api/products", json=payload, headers=admin_headers).json()


def test_agregar_y_ver_carrito_con_totales(client, admin_headers):
    prod = _crear_producto(client, admin_headers)
    headers = _registrar_login(client)

    r = client.post(
        "/api/cart/items",
        json={"product_id": prod["id"], "sku": "RUN-42", "quantity": 2},
        headers=headers,
    )
    assert r.status_code == 200
    cart = r.json()
    assert len(cart["lines"]) == 1
    assert cart["lines"][0]["quantity"] == 2
    assert cart["subtotal"] == 2000.0
    assert cart["tax"] == round(2000.0 * 0.16, 2)
    assert cart["total"] == cart["subtotal"] + cart["tax"] + cart["shipping"]


def test_merge_de_cantidad(client, admin_headers):
    prod = _crear_producto(client, admin_headers)
    headers = _registrar_login(client)
    body = {"product_id": prod["id"], "sku": "RUN-42", "quantity": 1}
    client.post("/api/cart/items", json=body, headers=headers)
    cart = client.post("/api/cart/items", json=body, headers=headers).json()
    assert cart["lines"][0]["quantity"] == 2


def test_checkout_exitoso_descuenta_stock(client, admin_headers):
    prod = _crear_producto(client, admin_headers)
    headers = _registrar_login(client)
    client.post(
        "/api/cart/items",
        json={"product_id": prod["id"], "sku": "RUN-42", "quantity": 2},
        headers=headers,
    )
    r = client.post(
        "/api/orders/checkout",
        json={"shipping_address": {"city": "CDMX"}},
        headers=headers,
    )
    assert r.status_code == 201
    order = r.json()
    assert order["status"] == "pending"
    assert order["total"] > 0
    assert len(order["lines"]) == 1

    # Stock descontado de 3 -> 1
    p = client.get(f"/api/products/{prod['id']}").json()
    assert p["variants"][0]["stock"] == 1
    # Carrito vaciado
    assert client.get("/api/cart", headers=headers).json()["lines"] == []
    # Aparece en el historial
    assert len(client.get("/api/orders", headers=headers).json()) == 1


def test_checkout_sin_stock_falla_sin_efectos(client, admin_headers):
    prod = _crear_producto(client, admin_headers)  # stock 3
    headers = _registrar_login(client)
    client.post(
        "/api/cart/items",
        json={"product_id": prod["id"], "sku": "RUN-42", "quantity": 5},
        headers=headers,
    )
    r = client.post("/api/orders/checkout", json={}, headers=headers)
    assert r.status_code == 409
    # No se creó pedido ni se descontó stock
    assert client.get("/api/orders", headers=headers).json() == []
    p = client.get(f"/api/products/{prod['id']}").json()
    assert p["variants"][0]["stock"] == 3


def test_anti_sobreventa_ultima_unidad(client, admin_headers):
    """Dos compradores compiten por la última unidad: solo uno gana."""
    prod = _crear_producto(
        client, admin_headers, variants=[{"sku": "U", "attrs": {}, "stock": 1}]
    )
    h1 = _registrar_login(client, email="c1@shop.mx")
    h2 = _registrar_login(client, email="c2@shop.mx")
    for h in (h1, h2):
        client.post(
            "/api/cart/items",
            json={"product_id": prod["id"], "sku": "U", "quantity": 1},
            headers=h,
        )
    r1 = client.post("/api/orders/checkout", json={}, headers=h1)
    r2 = client.post("/api/orders/checkout", json={}, headers=h2)
    exitos = [r for r in (r1, r2) if r.status_code == 201]
    fallos = [r for r in (r1, r2) if r.status_code == 409]
    assert len(exitos) == 1
    assert len(fallos) == 1
    # Stock final 0, nunca negativo
    p = client.get(f"/api/products/{prod['id']}").json()
    assert p["variants"][0]["stock"] == 0


def test_sync_carrito_invitado(client, admin_headers):
    prod = _crear_producto(client, admin_headers)
    headers = _registrar_login(client)
    r = client.post(
        "/api/cart/sync",
        json={"items": [{"product_id": prod["id"], "sku": "RUN-42", "quantity": 2}]},
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()["lines"][0]["quantity"] == 2
