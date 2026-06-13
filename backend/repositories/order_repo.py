"""Repositorio de pedidos con checkout transaccional (single-table DynamoDB).

El checkout usa TransactWriteItems: descuenta el stock de cada línea con condición
(stock_by_sku.<sku> >= qty) y crea el pedido, de forma atómica. Si algún stock es
insuficiente, la transacción completa se revierte (no se crea pedido ni se descuenta).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from boto3.dynamodb.conditions import Key
from boto3.dynamodb.types import TypeSerializer
from botocore.exceptions import ClientError

from backend.config import settings
from backend.db import keys
from backend.db.dynamo import get_client, get_table
from backend.db.serde import from_item, to_item
from backend.schemas.checkout import Order, OrderLine

_serializer = TypeSerializer()


class OutOfStockError(Exception):
    """Stock insuficiente para completar el checkout."""


def _ser(value):
    return _serializer.serialize(value)


def create_order(
    user_id: str,
    lines: list[OrderLine],
    totals: dict,
    shipping_address: dict,
) -> Order:
    """Crea el pedido y descuenta inventario atómicamente. Lanza OutOfStockError."""
    order_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    order = Order(
        id=order_id,
        user_id=user_id,
        lines=lines,
        shipping_address=shipping_address,
        created_at=created_at,
        **totals,
    )

    order_item = to_item(order.model_dump())
    order_item.update(
        {
            "PK": keys.user_pk(user_id),
            "SK": keys.order_sk(created_at, order_id),
            "entity": "order",
            **keys.order_gsi3(order.status, created_at, order_id),
        }
    )

    table_name = settings.DYNAMODB_TABLE
    transact_items = []
    for line in lines:
        transact_items.append(
            {
                "Update": {
                    "TableName": table_name,
                    "Key": {
                        "PK": _ser(keys.product_pk(line.product_id)),
                        "SK": _ser(keys.stock_sk(line.sku)),
                    },
                    "UpdateExpression": "SET #st = #st - :q",
                    "ConditionExpression": "#st >= :q",
                    "ExpressionAttributeNames": {"#st": "stock"},
                    "ExpressionAttributeValues": {":q": _ser(line.quantity)},
                }
            }
        )
    transact_items.append(
        {
            "Put": {
                "TableName": table_name,
                "Item": {k: _ser(v) for k, v in order_item.items()},
            }
        }
    )

    client = get_client()
    try:
        client.transact_write_items(TransactItems=transact_items)
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code", "")
        if code in ("TransactionCanceledException", "ConditionalCheckFailedException"):
            raise OutOfStockError(
                "Stock insuficiente para uno o más productos"
            ) from exc
        raise
    return order


def list_orders(user_id: str) -> list[Order]:
    resp = get_table().query(
        KeyConditionExpression=Key("PK").eq(keys.user_pk(user_id))
        & Key("SK").begins_with(keys.ORDER_SK_PREFIX),
        ScanIndexForward=False,
    )
    return [_to_order(from_item(it)) for it in resp.get("Items", [])]


def get_order(user_id: str, order_id: str) -> Order | None:
    for order in list_orders(user_id):
        if order.id == order_id:
            return order
    return None


def list_all() -> list[Order]:
    """Todos los pedidos del storefront (admin), vía GSI3 (GSI3PK=ORDERS)."""
    resp = get_table().query(
        IndexName="GSI3",
        KeyConditionExpression=Key("GSI3PK").eq("ORDERS"),
        ScanIndexForward=False,
    )
    return [_to_order(from_item(it)) for it in resp.get("Items", [])]


def _to_order(item: dict) -> Order:
    internal = ("PK", "SK", "entity", "GSI3PK", "GSI3SK")
    return Order(**{k: v for k, v in item.items() if k not in internal})
