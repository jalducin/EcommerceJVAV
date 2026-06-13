"""Reglas de fuente de verdad por entidad (configurable).

Define, por entidad (inventory/customers/orders), qué sistema manda. La sync respeta
estas reglas: el sistema fuente puede escribir; los subordinados no sobrescriben.
Se persiste como item único CONFIG/SOT en DynamoDB.
"""

from __future__ import annotations

from backend.db.dynamo import get_table

_PK = "CONFIG"
_SK = "SOT"

# Por defecto el núcleo canónico es la fuente de verdad de todo.
_DEFAULTS = {"inventory": "canonical", "customers": "canonical", "orders": "canonical"}


def get_rules() -> dict[str, str]:
    resp = get_table().get_item(Key={"PK": _PK, "SK": _SK})
    item = resp.get("Item") or {}
    rules = dict(_DEFAULTS)
    rules.update(item.get("rules", {}))
    return rules


def set_rule(entity: str, system: str) -> None:
    rules = get_rules()
    rules[entity] = system
    get_table().put_item(Item={"PK": _PK, "SK": _SK, "entity": "sot", "rules": rules})


def get_source(entity: str) -> str:
    return get_rules().get(entity, "canonical")


def is_source(entity: str, system: str) -> bool:
    """True si `system` es la fuente de verdad de `entity`."""
    return get_source(entity) == system
