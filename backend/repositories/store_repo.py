"""Repositorio de la configuración de tienda (item único CONFIG/STORE)."""

from __future__ import annotations

from backend.db import keys
from backend.db.dynamo import get_table
from backend.db.serde import from_item, to_item
from backend.schemas.store import StoreConfig


def get_config() -> StoreConfig:
    """Devuelve la configuración vigente; si no existe, los valores por defecto."""
    resp = get_table().get_item(Key={"PK": keys.CONFIG_PK, "SK": keys.CONFIG_SK})
    item = from_item(resp.get("Item"))
    if not item:
        return StoreConfig()
    item.pop("PK", None)
    item.pop("SK", None)
    item.pop("entity", None)
    return StoreConfig(**item)


def put_config(config: StoreConfig) -> StoreConfig:
    """Persiste (sobrescribe) la configuración de tienda."""
    item = to_item(config.model_dump())
    item.update({"PK": keys.CONFIG_PK, "SK": keys.CONFIG_SK, "entity": "config"})
    get_table().put_item(Item=item)
    return config
