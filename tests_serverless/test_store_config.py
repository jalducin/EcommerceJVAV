"""Tests de la capability store-configuration."""

from __future__ import annotations


def test_config_por_defecto(client):
    """Sin configurar, GET /api/config devuelve los valores por defecto (MetalShop)."""
    resp = client.get("/api/config")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "MetalShop"
    assert data["currency"] == "MXN"
    assert "gold" in data["theme"]


def test_config_persistida_y_business_agnostic(dynamo):
    """Cambiar la config a otro negocio se refleja sin tocar código."""
    from backend.repositories import store_repo
    from backend.schemas.store import StoreConfig

    nueva = StoreConfig(
        name="TecnoStore",
        categories=["laptops", "telefonos"],
        currency="USD",
        locale="en-US",
        tax_rate=0.08,
        theme={"primary": "#0A84FF"},
    )
    store_repo.put_config(nueva)

    leida = store_repo.get_config()
    assert leida.name == "TecnoStore"
    assert leida.currency == "USD"
    assert leida.categories == ["laptops", "telefonos"]
    assert leida.theme == {"primary": "#0A84FF"}
    assert leida.tax_rate == 0.08
