"""Tests de autenticación serverless (DynamoDB + JWT)."""

from __future__ import annotations


def _registrar(client, email="cliente@shop.mx", password="secret123"):
    return client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "full_name": "Cliente"},
    )


def test_registro_y_login(client):
    r = _registrar(client)
    assert r.status_code == 201
    body = r.json()
    assert body["email"] == "cliente@shop.mx"
    assert body["role"] == "client"
    assert "hashed_password" not in body

    login = client.post(
        "/api/auth/login", json={"email": "cliente@shop.mx", "password": "secret123"}
    )
    assert login.status_code == 200
    tokens = login.json()
    assert tokens["access_token"] and tokens["refresh_token"]


def test_email_duplicado_409(client):
    _registrar(client)
    assert _registrar(client).status_code == 409


def test_login_invalido_401(client):
    _registrar(client)
    bad = client.post(
        "/api/auth/login", json={"email": "cliente@shop.mx", "password": "incorrecta"}
    )
    assert bad.status_code == 401


def test_me_requiere_token(client):
    _registrar(client)
    tokens = client.post(
        "/api/auth/login", json={"email": "cliente@shop.mx", "password": "secret123"}
    ).json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    me = client.get("/api/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["email"] == "cliente@shop.mx"

    assert client.get("/api/auth/me").status_code in (401, 403)


def test_refresh_token(client):
    _registrar(client)
    tokens = client.post(
        "/api/auth/login", json={"email": "cliente@shop.mx", "password": "secret123"}
    ).json()
    r = client.post(
        "/api/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert r.status_code == 200
    assert r.json()["access_token"]
    # Un access token no sirve como refresh
    bad = client.post(
        "/api/auth/refresh", json={"refresh_token": tokens["access_token"]}
    )
    assert bad.status_code == 401


def test_admin_puede_crear_producto(client, admin_headers):
    resp = client.post(
        "/api/products",
        json={"name": "Gorra", "price": 299.0, "category": "ropa", "variants": []},
        headers=admin_headers,
    )
    assert resp.status_code == 201


def test_cliente_no_puede_crear_producto_403(client):
    _registrar(client, email="user2@shop.mx")
    tokens = client.post(
        "/api/auth/login", json={"email": "user2@shop.mx", "password": "secret123"}
    ).json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    resp = client.post(
        "/api/products",
        json={"name": "Gorra", "price": 299.0, "category": "ropa", "variants": []},
        headers=headers,
    )
    assert resp.status_code == 403
