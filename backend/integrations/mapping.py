"""Mapeo persistente de identificadores externo <-> canónico (por conector).

Doble escritura para resolver en ambos sentidos con GetItem O(1). Es la base de la
idempotencia/deduplicación de la ingesta (un id externo -> un único id canónico).
"""

from __future__ import annotations

from backend.db import keys
from backend.db.dynamo import get_table
from backend.integrations.canonical import EntityType


def set_mapping(
    connector: str, entity: EntityType, external_id: str, canonical_id: str
) -> None:
    table = get_table()
    ent = entity.value
    table.put_item(
        Item={
            "PK": keys.map_ext_pk(connector, ent),
            "SK": keys.map_ext_sk(external_id),
            "entity": "id_map",
            "connector": connector,
            "entity_type": ent,
            "external_id": external_id,
            "canonical_id": canonical_id,
        }
    )
    table.put_item(
        Item={
            "PK": keys.map_canon_pk(ent, canonical_id),
            "SK": keys.map_canon_sk(connector),
            "entity": "id_map",
            "connector": connector,
            "entity_type": ent,
            "external_id": external_id,
            "canonical_id": canonical_id,
        }
    )


def get_canonical_id(
    connector: str, entity: EntityType, external_id: str
) -> str | None:
    resp = get_table().get_item(
        Key={
            "PK": keys.map_ext_pk(connector, entity.value),
            "SK": keys.map_ext_sk(external_id),
        }
    )
    item = resp.get("Item")
    return item["canonical_id"] if item else None


def get_external_id(
    connector: str, entity: EntityType, canonical_id: str
) -> str | None:
    resp = get_table().get_item(
        Key={
            "PK": keys.map_canon_pk(entity.value, canonical_id),
            "SK": keys.map_canon_sk(connector),
        }
    )
    item = resp.get("Item")
    return item["external_id"] if item else None
