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
async def product_id(client: AsyncClient) -> int:
    """Crea un producto y devuelve su ID."""
    await client.post("/api/auth/register", json=ADMIN_PAYLOAD)
    login_res = await client.post(
        "/api/auth/login", data={"username": ADMIN_PAYLOAD["email"], "password": ADMIN_PAYLOAD["password"]}
    )
    admin_token = login_res.json()["access_token"]

    product_data = {"name": "Test Product for Cart", "price": 10.0, "stock": 100, "category": "test"}
    res = await client.post(
        "/api/products", json=product_data, headers={"Authorization": f"Bearer {admin_token}"}
    )
    return res.json()["id"]


async def test_add_item_to_cart(auth_client: AsyncClient, product_id: int):
    res = await auth_client.post("/api/cart/items", json={"product_id": product_id, "quantity": 2})
    assert res.status_code == 200
    data = res.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["product"]["id"] == product_id
    assert data["items"][0]["quantity"] == 2
    assert data["total"] == 20.0


async def test_add_same_item_merges_quantity(auth_client: AsyncClient, product_id: int):
    await auth_client.post("/api/cart/items", json={"product_id": product_id, "quantity": 1})
    res = await auth_client.post("/api/cart/items", json={"product_id": product_id, "quantity": 3})
    assert res.status_code == 200
    data = res.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["quantity"] == 4
    assert data["total"] == 40.0


async def test_get_cart(auth_client: AsyncClient, product_id: int):
    await auth_client.post("/api/cart/items", json={"product_id": product_id, "quantity": 5})
    res = await auth_client.get("/api/cart")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 50.0
    assert data["items"][0]["quantity"] == 5


async def test_update_cart_item(auth_client: AsyncClient, product_id: int):
    add_res = await auth_client.post("/api/cart/items", json={"product_id": product_id, "quantity": 1})
    cart_item_id = add_res.json()["items"][0]["id"]

    res = await auth_client.put(f"/api/cart/items/{cart_item_id}", json={"quantity": 10})
    assert res.status_code == 200
    data = res.json()
    assert data["items"][0]["quantity"] == 10
    assert data["total"] == 100.0


async def test_delete_cart_item(auth_client: AsyncClient, product_id: int):
    add_res = await auth_client.post("/api/cart/items", json={"product_id": product_id, "quantity": 1})
    cart_item_id = add_res.json()["items"][0]["id"]

    res = await auth_client.delete(f"/api/cart/items/{cart_item_id}")
    assert res.status_code == 200
    data = res.json()
    assert len(data["items"]) == 0
    assert data["total"] == 0.0