import pytest
from httpx import AsyncClient

from .test_auth import ADMIN_PAYLOAD, USER_PAYLOAD


@pytest.fixture
async def auth_client(client: AsyncClient) -> AsyncClient:
    """Cliente autenticado con rol de cliente."""
    await client.post("/api/auth/register", json=USER_PAYLOAD)
    login_res = await client.post(
        "/api/auth/login", data={"username": USER_PAYLOAD["email"], "password": USER_PAYLOAD["password"]}
    )
    token = login_res.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}
    return client


@pytest.fixture
async def product_in_stock(client: AsyncClient) -> dict:
    """Crea un producto con stock y devuelve su data."""
    await client.post("/api/auth/register", json=ADMIN_PAYLOAD)
    login_res = await client.post(
        "/api/auth/login", data={"username": ADMIN_PAYLOAD["email"], "password": ADMIN_PAYLOAD["password"]}
    )
    admin_token = login_res.json()["access_token"]

    product_data = {"name": "Checkout Product", "price": 50.0, "stock": 10, "category": "checkout"}
    res = await client.post(
        "/api/products", json=product_data, headers={"Authorization": f"Bearer {admin_token}"}
    )
    return res.json()


async def test_checkout_success(auth_client: AsyncClient, product_in_stock: dict):
    # 1. Añadir item al carrito
    product_id = product_in_stock["id"]
    await auth_client.post("/api/cart/items", json={"product_id": product_id, "quantity": 2})

    # 2. Checkout
    res = await auth_client.post("/api/orders/checkout", json={})
    assert res.status_code == 201
    order_data = res.json()
    assert order_data["total"] == 100.0
    assert order_data["status"] == "pending"

    # 3. Verificar que el stock se redujo
    product_res = await auth_client.get(f"/api/products/{product_id}")
    assert product_res.json()["stock"] == 8  # 10 - 2

    # 4. Verificar que el carrito está vacío
    cart_res = await auth_client.get("/api/cart")
    assert cart_res.json()["total"] == 0.0


async def test_checkout_insufficient_stock(auth_client: AsyncClient, product_in_stock: dict):
    product_id = product_in_stock["id"]
    # Intentar comprar más del stock disponible (10)
    await auth_client.post("/api/cart/items", json={"product_id": product_id, "quantity": 11})

    res = await auth_client.post("/api/orders/checkout", json={})
    # La validación de stock se hace en el checkout
    assert res.status_code == 409  # Conflict
    assert "stock" in res.json()["detail"].lower()


async def test_get_my_orders(auth_client: AsyncClient, product_in_stock: dict):
    # Crear un pedido
    await auth_client.post("/api/cart/items", json={"product_id": product_in_stock["id"], "quantity": 1})
    checkout_res = await auth_client.post("/api/orders/checkout", json={})
    order_id = checkout_res.json()["id"]

    # Obtener historial de pedidos
    res = await auth_client.get("/api/orders")
    assert res.status_code == 200
    orders = res.json()
    assert isinstance(orders, list)
    assert len(orders) >= 1
    assert orders[0]["id"] == order_id


async def test_get_single_order(auth_client: AsyncClient, product_in_stock: dict):
    # Crear un pedido
    await auth_client.post("/api/cart/items", json={"product_id": product_in_stock["id"], "quantity": 1})
    checkout_res = await auth_client.post("/api/orders/checkout", json={})
    order_id = checkout_res.json()["id"]

    # Obtener detalle del pedido
    res = await auth_client.get(f"/api/orders/{order_id}")
    assert res.status_code == 200
    order_detail = res.json()
    assert order_detail["id"] == order_id
    assert len(order_detail["items"]) == 1
    assert order_detail["items"][0]["product"]["id"] == product_in_stock["id"]