"""Tests de la capability catálogo (productos con variantes) sobre DynamoDB."""

from __future__ import annotations


def _nuevo_producto(client, headers, **over):
    payload = {
        "name": "Tenis Runner",
        "description": "Sneakers premium",
        "price": 1899.0,
        "category": "tenis",
        "images": ["https://example.com/a.jpg"],
        "variants": [
            {
                "sku": "RUN-42-NEG",
                "attrs": {"talla": "42", "color": "negro"},
                "stock": 5,
            },
            {
                "sku": "RUN-43-NEG",
                "attrs": {"talla": "43", "color": "negro"},
                "stock": 0,
            },
        ],
    }
    payload.update(over)
    return client.post("/api/products", json=payload, headers=headers)


def test_crear_y_obtener_producto_con_variantes(client, admin_headers):
    resp = _nuevo_producto(client, admin_headers)
    assert resp.status_code == 201
    prod = resp.json()
    assert prod["id"]
    assert len(prod["variants"]) == 2
    assert prod["variants"][0]["attrs"]["talla"] == "42"
    assert prod["price"] == 1899.0

    got = client.get(f"/api/products/{prod['id']}")
    assert got.status_code == 200
    assert got.json()["name"] == "Tenis Runner"


def test_crear_producto_sin_admin_falla_401(client):
    # Sin token -> 401 (HTTPBearer auto_error)
    resp = client.post(
        "/api/products", json={"name": "x", "price": 1, "category": "tenis"}
    )
    assert resp.status_code in (401, 403)


def test_producto_inexistente_404(client):
    assert client.get("/api/products/no-existe").status_code == 404


def test_listado_filtros_y_busqueda(client, admin_headers):
    _nuevo_producto(
        client, admin_headers, name="Tenis Runner", category="tenis", price=1899.0
    )
    _nuevo_producto(
        client,
        admin_headers,
        name="Playera Oversize",
        category="ropa",
        price=499.0,
        variants=[],
    )
    _nuevo_producto(
        client,
        admin_headers,
        name="Tenis Trail",
        category="tenis",
        price=2500.0,
        variants=[],
    )

    todos = client.get("/api/products").json()
    assert todos["total"] == 3

    tenis = client.get("/api/products", params={"category": "tenis"}).json()
    assert tenis["total"] == 2
    assert all(p["category"] == "tenis" for p in tenis["items"])

    runner = client.get("/api/products", params={"q": "runner"}).json()
    assert runner["total"] == 1
    assert runner["items"][0]["name"] == "Tenis Runner"

    baratos = client.get("/api/products", params={"max_price": 600}).json()
    assert baratos["total"] == 1
    assert baratos["items"][0]["name"] == "Playera Oversize"


def test_paginacion(client, admin_headers):
    for i in range(5):
        _nuevo_producto(
            client, admin_headers, name=f"Item {i}", category="tenis", variants=[]
        )
    page = client.get("/api/products", params={"limit": 2, "offset": 0}).json()
    assert page["total"] == 5
    assert len(page["items"]) == 2
    assert page["limit"] == 2


def test_categoria_invalida_rechazada(client, admin_headers):
    from backend.repositories import store_repo
    from backend.schemas.store import StoreConfig

    store_repo.put_config(StoreConfig(categories=["ropa", "tenis"]))
    resp = _nuevo_producto(client, admin_headers, category="electronica", variants=[])
    assert resp.status_code == 422


def test_update_y_soft_delete(client, admin_headers):
    pid = _nuevo_producto(client, admin_headers, variants=[]).json()["id"]

    upd = client.put(
        f"/api/products/{pid}", json={"price": 999.0}, headers=admin_headers
    )
    assert upd.status_code == 200
    assert upd.json()["price"] == 999.0

    assert (
        client.delete(f"/api/products/{pid}", headers=admin_headers).status_code == 204
    )
    assert client.get(f"/api/products/{pid}").status_code == 404
    assert client.get("/api/products").json()["total"] == 0
