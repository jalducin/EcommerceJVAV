import pytest
from httpx import AsyncClient

from .test_auth import ADMIN_PAYLOAD, USER_PAYLOAD

PRODUCT_PAYLOAD = {
    "name": "Heavy Metal Wrench",
    "description": "A very heavy wrench.",
    "price": 99.99,
    "stock": 50,
    "category": "tools",
    "images": ["url1.jpg", "url2.jpg"],
}


@pytest.fixture
async def admin_client(client: AsyncClient) -> AsyncClient:
    """Cliente autenticado con rol de administrador."""
    # Nota: Se asume que el setup de tests o una migración crea un usuario admin
    # o que el servicio de registro asigna el rol 'admin' basado en el email.
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


# ─── Product CRUD (Admin) ─────────────────────────────────────────────────────


async def test_create_product_as_admin(admin_client: AsyncClient):
    res = await admin_client.post("/api/products", json=PRODUCT_PAYLOAD)
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == PRODUCT_PAYLOAD["name"]
    assert data["stock"] == 50


async def test_create_product_as_client_fails(regular_client: AsyncClient):
    res = await regular_client.post("/api/products", json=PRODUCT_PAYLOAD)
    assert res.status_code == 403  # Forbidden


async def test_update_product_as_admin(admin_client: AsyncClient):
    create_res = await admin_client.post("/api/products", json=PRODUCT_PAYLOAD)
    product_id = create_res.json()["id"]

    update_payload = {"price": 120.50, "stock": 45}
    res = await admin_client.put(f"/api/products/{product_id}", json=update_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["price"] == 120.50
    assert data["stock"] == 45


async def test_delete_product_as_admin(admin_client: AsyncClient):
    create_res = await admin_client.post("/api/products", json=PRODUCT_PAYLOAD)
    product_id = create_res.json()["id"]

    res = await admin_client.delete(f"/api/products/{product_id}")
    assert res.status_code == 204

    get_res = await admin_client.get(f"/api/products/{product_id}")
    assert get_res.status_code == 404


# ─── Product Listing (Public) ─────────────────────────────────────────────────


@pytest.fixture(scope="module", autouse=True)
async def seed_products(client: AsyncClient):
    """Puebla la BD con productos para los tests de listado."""
    # Se necesita un cliente admin para crear productos
    await client.post("/api/auth/register", json=ADMIN_PAYLOAD)
    login_res = await client.post(
        "/api/auth/login", data={"username": ADMIN_PAYLOAD["email"], "password": ADMIN_PAYLOAD["password"]}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    products = [
        {"name": "Iron Hammer", "price": 25.0, "category": "tools", "stock": 100},
        {"name": "Steel Plate", "price": 150.0, "category": "materials", "stock": 20},
        {"name": "Copper Wire", "price": 75.0, "category": "materials", "stock": 5},
    ]
    for p in products:
        await client.post("/api/products", json={**PRODUCT_PAYLOAD, **p}, headers=headers)
    yield


async def test_get_products_list(client: AsyncClient):
    res = await client.get("/api/products")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 3


async def test_products_pagination(client: AsyncClient):
    res = await client.get("/api/products?limit=2&offset=1")
    assert res.status_code == 200
    data = res.json()
    assert len(data["items"]) == 2


async def test_products_filtering_by_category(client: AsyncClient):
    res = await client.get("/api/products?category=materials")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 2
    for item in data["items"]:
        assert item["category"] == "materials"


async def test_products_search(client: AsyncClient):
    res = await client.get("/api/products?search=plate")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Steel Plate"