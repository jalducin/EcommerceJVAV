"""Lógica de gestión de categorías de tienda (persisten en store-config)."""

from __future__ import annotations

from backend.repositories import product_repo, store_repo


def list_categories() -> list[str]:
    return store_repo.get_config().categories


def add_category(name: str) -> list[str]:
    """Agrega una categoría idempotente (trim, sin duplicados case-insensitive)."""
    clean = name.strip()
    config = store_repo.get_config()
    existing_lower = {c.lower() for c in config.categories}
    if clean.lower() not in existing_lower:
        config.categories = [*config.categories, clean]
        store_repo.put_config(config)
    return config.categories


def category_in_use(name: str) -> bool:
    """True si algún producto activo usa la categoría."""
    return product_repo.list_products(category=name, limit=1).total > 0


def remove_category(name: str) -> list[str]:
    """Elimina una categoría (insensible a mayúsculas). El router valida el uso."""
    config = store_repo.get_config()
    config.categories = [
        c for c in config.categories if c.lower() != name.strip().lower()
    ]
    store_repo.put_config(config)
    return config.categories
