"""Tests: gestión de categorías e imágenes (presigned upload) en el panel admin."""

from __future__ import annotations

import pytest


@pytest.fixture
def user_headers(client):
    """Usuario normal (no admin) para probar autorización."""
    from backend.repositories import user_repo
    from backend.schemas.account import UserCreate

    user_repo.create_user(
        UserCreate(email="cliente@shop.mx", password="clientpass", full_name="Cliente"),
    )
    resp = client.post(
        "/api/auth/login",
        json={"email": "cliente@shop.mx", "password": "clientpass"},
    )
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


# ── Categorías ──────────────────────────────────────────────────────────────


def test_agregar_y_listar_categoria(client, admin_headers):
    resp = client.post(
        "/api/admin/categories", json={"name": "tenis"}, headers=admin_headers
    )
    assert resp.status_code == 201
    assert "tenis" in resp.json()["categories"]

    listed = client.get("/api/admin/categories", headers=admin_headers)
    assert listed.status_code == 200
    assert "tenis" in listed.json()["categories"]


def test_agregar_categoria_es_idempotente(client, admin_headers):
    client.post("/api/admin/categories", json={"name": "Ropa"}, headers=admin_headers)
    # Mismo nombre con distinto casing y espacios: no debe duplicar.
    resp = client.post(
        "/api/admin/categories", json={"name": " ropa "}, headers=admin_headers
    )
    cats = resp.json()["categories"]
    assert sum(1 for c in cats if c.lower() == "ropa") == 1


def test_eliminar_categoria_sin_uso(client, admin_headers):
    client.post("/api/admin/categories", json={"name": "vacia"}, headers=admin_headers)
    resp = client.delete("/api/admin/categories/vacia", headers=admin_headers)
    assert resp.status_code == 204
    listed = client.get("/api/admin/categories", headers=admin_headers).json()
    assert "vacia" not in listed["categories"]


def test_eliminar_categoria_en_uso_devuelve_409(client, admin_headers):
    client.post("/api/admin/categories", json={"name": "tenis"}, headers=admin_headers)
    prod = client.post(
        "/api/products",
        json={"name": "Runner", "price": 1899.0, "category": "tenis"},
        headers=admin_headers,
    )
    assert prod.status_code == 201
    resp = client.delete("/api/admin/categories/tenis", headers=admin_headers)
    assert resp.status_code == 409
    # La categoría sigue existiendo.
    listed = client.get("/api/admin/categories", headers=admin_headers).json()
    assert "tenis" in listed["categories"]


def test_categorias_requiere_admin(client, user_headers):
    con_user = client.get("/api/admin/categories", headers=user_headers)
    assert con_user.status_code == 403
    sin_auth = client.get("/api/admin/categories")
    assert sin_auth.status_code in (401, 403)


# ── Presigned upload ────────────────────────────────────────────────────────


def test_presign_imagen_valida(client, admin_headers, monkeypatch):
    from backend.config import settings

    monkeypatch.setattr(settings, "MEDIA_BUCKET", "metalshop-frontend-dev-123")
    monkeypatch.setattr(settings, "MEDIA_PUBLIC_BASE", "https://cdn.example.com")

    resp = client.post(
        "/api/admin/uploads/presign",
        json={"filename": "foto.png", "content_type": "image/png"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["key"].startswith("media/")
    assert body["key"].endswith(".png")
    assert body["public_url"].startswith("https://cdn.example.com/media/")
    assert "http" in body["upload_url"]


def test_presign_tipo_no_permitido(client, admin_headers, monkeypatch):
    from backend.config import settings

    monkeypatch.setattr(settings, "MEDIA_BUCKET", "metalshop-frontend-dev-123")
    resp = client.post(
        "/api/admin/uploads/presign",
        json={"filename": "doc.pdf", "content_type": "application/pdf"},
        headers=admin_headers,
    )
    assert resp.status_code == 422


def test_presign_requiere_admin(client, user_headers):
    payload = {"filename": "f.png", "content_type": "image/png"}
    con_user = client.post(
        "/api/admin/uploads/presign", json=payload, headers=user_headers
    )
    assert con_user.status_code == 403
    sin_auth = client.post("/api/admin/uploads/presign", json=payload)
    assert sin_auth.status_code in (401, 403)
