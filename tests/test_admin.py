import pytest
from httpx import AsyncClient

from .test_auth import ADMIN_PAYLOAD, USER_PAYLOAD


@pytest.fixture
async def admin_client(client: AsyncClient) -> AsyncClient:
    """Cliente autenticado con rol de administrador."""
    await client.post("/api/auth/register", json=ADMIN_PAYLOAD)
    login_res = await client.post(
        "/api/auth/login", data={"username": ADMIN_PAYLOAD["email"], "password": ADMIN_PAYLOAD["password"]}
    )
    token = login_res.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}
    return client


@pytest.fixture
async def regular_client(client: AsyncClient) -> AsyncClient:
    """Cliente autenticado con rol de cliente."""
    await client.post("/api/auth/register", json=USER_PAYLOAD)
    login_res = await client.post(
        "/api/auth/login", data={"username": USER_PAYLOAD["email"], "password": USER_PAYLOAD["password"]}
    )
    token = login_res.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}
    return client


@pytest.fixture
async def created_order_id(regular_client: AsyncClient, client: AsyncClient) -> int:
    """Crea un producto y un pedido, y devuelve el ID del pedido."""
    # Se necesita un admin para crear el producto
    await client.post("/api/auth/register", json=ADMIN_PAYLOAD)
    login_res = await client.post(
        "/api/auth/login", data={"username": ADMIN_PAYLOAD["email"], "password": ADMIN_PAYLOAD["password"]}
    )
    admin_token = login_res.json()["access_token"]
    product_data = {"name": "Order Product", "price": 10.0, "stock": 10, "category": "test"}
    prod_res = await client.post(
        "/api/products", json=product_data, headers={"Authorization": f"Bearer {admin_token}"}
    )
    product_id = prod_res.json()["id"]

    # El cliente regular hace el pedido
    await regular_client.post("/api/cart/items", json={"product_id": product_id, "quantity": 1})
    checkout_res = await regular_client.post("/api/orders/checkout", json={})
    return checkout_res.json()["id"]


async def test_get_dashboard_as_admin(admin_client: AsyncClient):
    res = await admin_client.get("/api/admin/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert "daily_sales" in data


async def test_get_dashboard_as_client_fails(regular_client: AsyncClient):
    res = await regular_client.get("/api/admin/dashboard")
    assert res.status_code == 403


async def test_list_all_orders_as_admin(admin_client: AsyncClient, created_order_id: int):
    res = await admin_client.get("/api/admin/orders")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    assert any(order["id"] == created_order_id for order in data["items"])


async def test_list_all_orders_as_client_fails(regular_client: AsyncClient):
    res = await regular_client.get("/api/admin/orders")
    assert res.status_code == 403


async def test_change_order_status_as_admin(admin_client: AsyncClient, created_order_id: int):
    res = await admin_client.patch(
        f"/api/admin/orders/{created_order_id}/status", json={"status": "shipped"}
    )
    assert res.status_code == 200
    assert res.json()["status"] == "shipped"