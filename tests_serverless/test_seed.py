"""Tests del cargador de datos demo (idempotente)."""

from __future__ import annotations


def test_seed_idempotente(dynamo):
    from backend.repositories import product_repo, store_repo, user_repo
    from seed_dynamodb import seed

    r1 = seed()
    assert r1["products"] == 12
    assert r1["admin_created"] is True

    # Config y productos sembrados
    cfg = store_repo.get_config()
    assert cfg.name == "MetalShop"
    assert "tenis" in cfg.categories
    todos = product_repo.list_products(limit=100)
    assert todos.total == 12

    # Re-ejecutar no duplica ni recrea el admin
    r2 = seed()
    assert r2["admin_created"] is False
    assert product_repo.list_products(limit=100).total == 12
    assert user_repo.get_user_by_email("admin@metalshop.mx") is not None


def test_seed_dataset_alternativo(dynamo):
    """Otro vertical (electrónica) sin cambiar código."""
    from backend.repositories import product_repo, store_repo
    from backend.schemas.catalog import Product
    from backend.schemas.store import StoreConfig
    from seed_dynamodb import seed

    config = StoreConfig(name="TecnoStore", categories=["laptops"], currency="USD")
    productos = [
        Product(
            id="lap-1",
            name="Laptop Pro",
            price=25000.0,
            category="laptops",
            stock=3,
            created_at="2026-01-01T00:00:00+00:00",
        )
    ]
    r = seed(config=config, products=productos, admin=None)
    assert r["products"] == 1
    assert store_repo.get_config().name == "TecnoStore"
    p = product_repo.list_products(category="laptops").items[0]
    assert p.name == "Laptop Pro"
    assert p.stock == 3
