import pytest
from httpx import AsyncClient


# ─── Helpers ──────────────────────────────────────────────────────────────────

USER_PAYLOAD = {
    "email": "test@metalshop.com",
    "password": "password123",
    "full_name": "Test User",
}

ADMIN_PAYLOAD = {
    "email": "admin@metalshop.com",
    "password": "adminpass123",
    "full_name": "Admin User",
}


# ─── Register ─────────────────────────────────────────────────────────────────


async def test_register_success(client: AsyncClient):
    res = await client.post("/api/auth/register", json=USER_PAYLOAD)
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == USER_PAYLOAD["email"]
    assert data["full_name"] == USER_PAYLOAD["full_name"]
    assert data["role"] == "client"
    assert data["is_active"] is True
    assert "id" in data
    assert "hashed_password" not in data


async def test_register_duplicate_email(client: AsyncClient):
    await client.post("/api/auth/register", json=USER_PAYLOAD)
    res = await client.post("/api/auth/register", json=USER_PAYLOAD)
    assert res.status_code == 400
    assert "email" in res.json()["detail"].lower()


async def test_register_invalid_email(client: AsyncClient):
    res = await client.post(
        "/api/auth/register",
        json={**USER_PAYLOAD, "email": "not-an-email"},
    )
    assert res.status_code == 422


async def test_register_short_password(client: AsyncClient):
    res = await client.post(
        "/api/auth/register",
        json={**USER_PAYLOAD, "email": "new@metalshop.com", "password": "short"},
    )
    assert res.status_code == 422


# ─── Login ────────────────────────────────────────────────────────────────────


async def test_login_success(client: AsyncClient):
    await client.post("/api/auth/register", json=USER_PAYLOAD)
    res = await client.post(
        "/api/auth/login",
        json={"email": USER_PAYLOAD["email"], "password": USER_PAYLOAD["password"]},
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password(client: AsyncClient):
    await client.post("/api/auth/register", json=USER_PAYLOAD)
    res = await client.post(
        "/api/auth/login",
        json={"email": USER_PAYLOAD["email"], "password": "wrongpassword"},
    )
    assert res.status_code == 401


async def test_login_unknown_email(client: AsyncClient):
    res = await client.post(
        "/api/auth/login",
        json={"email": "noexiste@metalshop.com", "password": "password123"},
    )
    assert res.status_code == 401


# ─── Refresh ──────────────────────────────────────────────────────────────────


async def test_refresh_success(client: AsyncClient):
    await client.post("/api/auth/register", json=USER_PAYLOAD)
    login_res = await client.post(
        "/api/auth/login",
        json={"email": USER_PAYLOAD["email"], "password": USER_PAYLOAD["password"]},
    )
    refresh_token = login_res.json()["refresh_token"]

    res = await client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert res.status_code == 200
    assert "access_token" in res.json()


async def test_refresh_invalid_token(client: AsyncClient):
    res = await client.post("/api/auth/refresh", json={"refresh_token": "token.invalido.fake"})
    assert res.status_code == 401


async def test_refresh_with_access_token_fails(client: AsyncClient):
    """Un access token no debe ser válido como refresh token."""
    await client.post("/api/auth/register", json=USER_PAYLOAD)
    login_res = await client.post(
        "/api/auth/login",
        json={"email": USER_PAYLOAD["email"], "password": USER_PAYLOAD["password"]},
    )
    access_token = login_res.json()["access_token"]

    res = await client.post("/api/auth/refresh", json={"refresh_token": access_token})
    assert res.status_code == 401


# ─── Me (ruta protegida) ──────────────────────────────────────────────────────


async def test_get_me_authenticated(client: AsyncClient):
    await client.post("/api/auth/register", json=USER_PAYLOAD)
    login_res = await client.post(
        "/api/auth/login",
        json={"email": USER_PAYLOAD["email"], "password": USER_PAYLOAD["password"]},
    )
    access_token = login_res.json()["access_token"]

    res = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert res.status_code == 200
    assert res.json()["email"] == USER_PAYLOAD["email"]


async def test_get_me_no_token(client: AsyncClient):
    res = await client.get("/api/auth/me")
    assert res.status_code == 403


async def test_get_me_invalid_token(client: AsyncClient):
    res = await client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer token.invalido.fake"},
    )
    assert res.status_code == 401
