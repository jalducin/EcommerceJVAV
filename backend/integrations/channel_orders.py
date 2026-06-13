"""Hub de pedidos unificado: persistencia de pedidos canónicos de cualquier canal.

PK = CHORDER#<canonical_id>, SK = ORDER. GSI3 (ORDERS) permite listarlos para admin.
"""

from __future__ import annotations

from boto3.dynamodb.conditions import Key

from backend.db.dynamo import get_table
from backend.db.serde import from_item, to_item
from backend.integrations.canonical import CanonicalOrder


def _pk(canonical_id: str) -> str:
    return f"CHORDER#{canonical_id}"


def save_order(order: CanonicalOrder) -> None:
    item = to_item(order.model_dump())
    item.update(
        {
            "PK": _pk(order.canonical_id),
            "SK": "ORDER",
            "entity": "channel_order",
            "GSI3PK": "CHANNELORDERS",
            "GSI3SK": f"{order.channel}#{order.canonical_id}",
        }
    )
    get_table().put_item(Item=item)


def get_order(canonical_id: str) -> CanonicalOrder | None:
    resp = get_table().get_item(Key={"PK": _pk(canonical_id), "SK": "ORDER"})
    item = from_item(resp.get("Item"))
    if not item:
        return None
    internal = ("PK", "SK", "entity", "GSI3PK", "GSI3SK")
    return CanonicalOrder(**{k: v for k, v in item.items() if k not in internal})


def list_orders(channel: str | None = None) -> list[CanonicalOrder]:
    kwargs = {
        "IndexName": "GSI3",
        "KeyConditionExpression": Key("GSI3PK").eq("CHANNELORDERS"),
    }
    if channel:
        kwargs["KeyConditionExpression"] = Key("GSI3PK").eq("CHANNELORDERS") & Key(
            "GSI3SK"
        ).begins_with(f"{channel}#")
    resp = get_table().query(**kwargs)
    internal = ("PK", "SK", "entity", "GSI3PK", "GSI3SK")
    return [
        CanonicalOrder(**{k: v for k, v in from_item(it).items() if k not in internal})
        for it in resp.get("Items", [])
    ]
