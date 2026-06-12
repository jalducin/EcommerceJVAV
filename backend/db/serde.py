"""Serialización entre dicts de Python y items de DynamoDB.

DynamoDB (boto3 resource) exige `Decimal` para números, no `float`. Estos helpers
convierten en ambos sentidos de forma recursiva.
"""

from __future__ import annotations

import json
from decimal import Decimal
from typing import Any


def to_item(data: dict) -> dict:
    """Convierte un dict con floats a un item DynamoDB (floats -> Decimal)."""
    return json.loads(json.dumps(data, default=str), parse_float=Decimal)


def _decode(value: Any) -> Any:
    if isinstance(value, Decimal):
        # Entero exacto -> int; si no, float.
        return int(value) if value % 1 == 0 else float(value)
    if isinstance(value, list):
        return [_decode(v) for v in value]
    if isinstance(value, dict):
        return {k: _decode(v) for k, v in value.items()}
    return value


def from_item(item: dict | None) -> dict | None:
    """Convierte un item de DynamoDB (con Decimal) a un dict de Python normal."""
    if item is None:
        return None
    return {k: _decode(v) for k, v in item.items()}
