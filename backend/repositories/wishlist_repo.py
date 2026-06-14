"""Repositorio de lista de deseos (single-table DynamoDB).

WishItem: PK=USER#<id>, SK=WISH#<product_id>. Idempotente.
"""

from __future__ import annotations

from datetime import datetime, timezone

from boto3.dynamodb.conditions import Key

from backend.db import keys
from backend.db.dynamo import get_table
from backend.db.serde import from_item


def add(user_id: str, product_id: str) -> None:
    get_table().put_item(
        Item={
            "PK": keys.user_pk(user_id),
            "SK": keys.wish_sk(product_id),
            "entity": "wishlist",
            "product_id": product_id,
            "added_at": datetime.now(timezone.utc).isoformat(),
        }
    )


def remove(user_id: str, product_id: str) -> None:
    get_table().delete_item(
        Key={"PK": keys.user_pk(user_id), "SK": keys.wish_sk(product_id)}
    )


def list_product_ids(user_id: str) -> list[str]:
    resp = get_table().query(
        KeyConditionExpression=Key("PK").eq(keys.user_pk(user_id))
        & Key("SK").begins_with(keys.WISH_SK_PREFIX)
    )
    return [from_item(it)["product_id"] for it in resp.get("Items", [])]
