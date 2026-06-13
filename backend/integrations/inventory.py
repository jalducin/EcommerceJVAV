"""Inventario unificado: operaciones sobre los items STOCK#<sku> del catálogo.

El inventario canónico (los items STOCK# del producto) es la fuente de verdad. Las
ventas online (storefront/checkout) descuentan con condición (anti-sobreventa); la
ingesta de pedidos de canales externos **refleja** la baja (el pedido ya ocurrió).
"""

from __future__ import annotations

from boto3.dynamodb.conditions import Attr

from backend.db import keys
from backend.db.dynamo import get_table


def find_product_id_by_sku(sku: str) -> str | None:
    """Resuelve el producto dueño de un sku (scan acotado de items STOCK#)."""
    resp = get_table().scan(
        FilterExpression=Attr("entity").eq("stock") & Attr("sku").eq(sku)
    )
    items = resp.get("Items", [])
    return items[0]["product_id"] if items else None


def get_stock(product_id: str, sku: str = "-") -> int | None:
    resp = get_table().get_item(
        Key={"PK": keys.product_pk(product_id), "SK": keys.stock_sk(sku)}
    )
    item = resp.get("Item")
    return int(item["stock"]) if item else None


def decrement_strict(product_id: str, sku: str, qty: int) -> bool:
    """Descuenta solo si hay stock suficiente (condicional). True si tuvo éxito."""
    from botocore.exceptions import ClientError

    try:
        get_table().update_item(
            Key={"PK": keys.product_pk(product_id), "SK": keys.stock_sk(sku)},
            UpdateExpression="SET stock = stock - :q",
            ConditionExpression=Attr("stock").gte(qty),
            ExpressionAttributeValues={":q": qty},
        )
        return True
    except ClientError as exc:
        if (
            exc.response.get("Error", {}).get("Code")
            == "ConditionalCheckFailedException"
        ):
            return False
        raise


def reflect_sale(product_id: str, sku: str, qty: int) -> int:
    """Refleja una venta externa: baja el stock sin pasar de 0; devuelve el nivel."""
    current = get_stock(product_id, sku)
    if current is None:
        return 0
    new_level = max(0, current - qty)
    get_table().update_item(
        Key={"PK": keys.product_pk(product_id), "SK": keys.stock_sk(sku)},
        UpdateExpression="SET stock = :n",
        ExpressionAttributeValues={":n": new_level},
    )
    return new_level
