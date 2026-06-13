"""Lógica del panel de administración: dashboard, pedidos unificados, conectores."""

from __future__ import annotations

from boto3.dynamodb.conditions import Attr

from backend.db.dynamo import get_table
from backend.db.serde import from_item
from backend.integrations import channel_orders
from backend.integrations.catalog_connectors import all_connectors
from backend.repositories import order_repo, product_repo

LOW_STOCK_THRESHOLD = 5


def low_stock_products(threshold: int = LOW_STOCK_THRESHOLD) -> list[dict]:
    """Productos activos con stock total por debajo del umbral."""
    out = []
    for p in product_repo.list_products(limit=1000).items:
        stock = p.total_stock
        if stock < threshold:
            out.append(
                {"id": p.id, "name": p.name, "stock": stock, "category": p.category}
            )
    return out


def unified_orders() -> list[dict]:
    """Pedidos del storefront + de canales, en una forma común para el admin."""
    rows: list[dict] = []
    for o in order_repo.list_all():
        rows.append(
            {
                "id": o.id,
                "source": "storefront",
                "channel": o.channel,
                "status": o.status,
                "total": o.total,
                "currency": o.currency,
            }
        )
    for o in channel_orders.list_orders():
        rows.append(
            {
                "id": o.canonical_id,
                "source": "channel",
                "channel": o.channel,
                "status": o.status,
                "total": o.total,
                "currency": o.currency,
            }
        )
    return rows


def dashboard() -> dict:
    orders = unified_orders()
    sales_total = round(sum(o["total"] for o in orders), 2)
    pending = sum(
        1 for o in orders if str(o["status"]).lower() in ("pending", "pendiente")
    )
    low = low_stock_products()
    connectors = all_connectors()
    return {
        "orders_count": len(orders),
        "sales_total": sales_total,
        "pending_orders": pending,
        "low_stock_count": len(low),
        "low_stock": low,
        "connectors": {
            "total": len(connectors),
            "available": sum(1 for c in connectors if not c["deferred"]),
            "deferred": sum(1 for c in connectors if c["deferred"]),
        },
    }


def set_channel_order_status(canonical_id: str, status: str) -> bool:
    """Cambia el estado de un pedido de canal en el hub unificado."""
    pk = f"CHORDER#{canonical_id}"
    resp = get_table().get_item(Key={"PK": pk, "SK": "ORDER"})
    if not from_item(resp.get("Item")):
        return False
    get_table().update_item(
        Key={"PK": pk, "SK": "ORDER"},
        UpdateExpression="SET #s = :st",
        ConditionExpression=Attr("PK").exists(),
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":st": status},
    )
    return True
