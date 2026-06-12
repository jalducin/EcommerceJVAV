"""Repositorio de carrito (single-table DynamoDB).

CartItem: PK=USER#<id>, SK=CART#<product_id>#<sku>. Cantidad acumulable (merge).
"""

from __future__ import annotations

from boto3.dynamodb.conditions import Key

from backend.db import keys
from backend.db.dynamo import get_table
from backend.db.serde import from_item
from backend.schemas.checkout import CartItemIn


def _sk(product_id: str, sku: str) -> str:
    return keys.cart_sk(product_id, sku)


def add_item(user_id: str, item: CartItemIn) -> None:
    """Agrega un item; si ya existe (product_id+sku), suma la cantidad (merge)."""
    table = get_table()
    sk = _sk(item.product_id, item.sku)
    existing = table.get_item(Key={"PK": keys.user_pk(user_id), "SK": sk}).get("Item")
    quantity = item.quantity + (int(existing["quantity"]) if existing else 0)
    table.put_item(
        Item={
            "PK": keys.user_pk(user_id),
            "SK": sk,
            "entity": "cart",
            "product_id": item.product_id,
            "sku": item.sku,
            "quantity": quantity,
        }
    )


def set_quantity(user_id: str, product_id: str, sku: str, quantity: int) -> None:
    table = get_table()
    if quantity <= 0:
        delete_item(user_id, product_id, sku)
        return
    table.put_item(
        Item={
            "PK": keys.user_pk(user_id),
            "SK": _sk(product_id, sku),
            "entity": "cart",
            "product_id": product_id,
            "sku": sku,
            "quantity": quantity,
        }
    )


def delete_item(user_id: str, product_id: str, sku: str) -> None:
    get_table().delete_item(
        Key={"PK": keys.user_pk(user_id), "SK": _sk(product_id, sku)}
    )


def list_items(user_id: str) -> list[dict]:
    resp = get_table().query(
        KeyConditionExpression=Key("PK").eq(keys.user_pk(user_id))
        & Key("SK").begins_with(keys.CART_SK_PREFIX)
    )
    return [from_item(it) for it in resp.get("Items", [])]


def clear(user_id: str) -> None:
    table = get_table()
    for it in list_items(user_id):
        table.delete_item(
            Key={"PK": keys.user_pk(user_id), "SK": _sk(it["product_id"], it["sku"])}
        )


def sync(user_id: str, items: list[CartItemIn]) -> None:
    """Fusiona items de invitado (localStorage) con el carrito en BD."""
    for item in items:
        add_item(user_id, item)
