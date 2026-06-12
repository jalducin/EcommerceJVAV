"""Repositorio de productos (single-table DynamoDB).

Listado por categoría vía GSI2; listado global y búsqueda por nombre vía Scan acotado
(aceptable para catálogos pequeños, ver design del cambio migrate-to-serverless-aws).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from boto3.dynamodb.conditions import Attr, Key

from backend.db import keys
from backend.db.dynamo import get_table
from backend.db.serde import from_item, to_item
from backend.schemas.catalog import Product, ProductCreate, ProductList, ProductUpdate


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


_INTERNAL = ("PK", "SK", "entity", "GSI2PK", "GSI2SK")


def _stock_map(product: Product) -> dict[str, int]:
    """sku -> stock; fuente de verdad del inventario ("-" si no hay variantes)."""
    if product.variants:
        return {v.sku: v.stock for v in product.variants}
    return {"-": product.stock}


def _to_product(item: dict) -> Product:
    data = {k: v for k, v in item.items() if k not in _INTERNAL}
    return Product(**data)


def get_stocks(product_id: str) -> dict[str, int]:
    """Lee los niveles de stock por sku desde los items de inventario."""
    resp = get_table().query(
        KeyConditionExpression=Key("PK").eq(keys.product_pk(product_id))
        & Key("SK").begins_with(keys.STOCK_SK_PREFIX)
    )
    stocks: dict[str, int] = {}
    for it in resp.get("Items", []):
        item = from_item(it)
        stocks[item["sku"]] = int(item["stock"])
    return stocks


def _hydrate(product: Product) -> Product:
    """Sobrescribe el stock del producto con la fuente de verdad (items STOCK#)."""
    stocks = get_stocks(product.id)
    if product.variants:
        for v in product.variants:
            v.stock = int(stocks.get(v.sku, v.stock))
    elif "-" in stocks:
        product.stock = int(stocks["-"])
    return product


def _item_for(product: Product) -> dict:
    item = to_item(product.model_dump())
    item.update(
        {
            "PK": keys.product_pk(product.id),
            "SK": keys.PRODUCT_SK,
            "entity": "product",
            **keys.product_gsi2(product.category, product.id),
        }
    )
    return item


def _write_stock_items(product: Product) -> None:
    table = get_table()
    for sku, stock in _stock_map(product).items():
        table.put_item(
            Item={
                "PK": keys.product_pk(product.id),
                "SK": keys.stock_sk(sku),
                "entity": "stock",
                "product_id": product.id,
                "sku": sku,
                "stock": int(stock),
            }
        )


def create_product(data: ProductCreate) -> Product:
    product = Product(id=str(uuid.uuid4()), created_at=_now(), **data.model_dump())
    get_table().put_item(Item=_item_for(product))
    _write_stock_items(product)
    return product


def get_product(product_id: str) -> Product | None:
    resp = get_table().get_item(
        Key={"PK": keys.product_pk(product_id), "SK": keys.PRODUCT_SK}
    )
    item = from_item(resp.get("Item"))
    return _hydrate(_to_product(item)) if item else None


def _scan_all() -> list[dict]:
    table = get_table()
    items: list[dict] = []
    kwargs = {"FilterExpression": Attr("entity").eq("product")}
    while True:
        resp = table.scan(**kwargs)
        items.extend(resp.get("Items", []))
        if "LastEvaluatedKey" not in resp:
            break
        kwargs["ExclusiveStartKey"] = resp["LastEvaluatedKey"]
    return items


def _query_category(category: str) -> list[dict]:
    table = get_table()
    items: list[dict] = []
    kwargs = {
        "IndexName": "GSI2",
        "KeyConditionExpression": Key("GSI2PK").eq(f"CAT#{category}"),
    }
    while True:
        resp = table.query(**kwargs)
        items.extend(resp.get("Items", []))
        if "LastEvaluatedKey" not in resp:
            break
        kwargs["ExclusiveStartKey"] = resp["LastEvaluatedKey"]
    return items


def list_products(
    *,
    category: str | None = None,
    q: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    active_only: bool = True,
    limit: int = 12,
    offset: int = 0,
) -> ProductList:
    raw = _query_category(category) if category else _scan_all()
    products = [_hydrate(_to_product(from_item(it))) for it in raw]

    if active_only:
        products = [p for p in products if p.is_active]
    if q:
        ql = q.lower()
        products = [p for p in products if ql in p.name.lower()]
    if min_price is not None:
        products = [p for p in products if p.price >= min_price]
    if max_price is not None:
        products = [p for p in products if p.price <= max_price]

    products.sort(key=lambda p: p.created_at, reverse=True)
    total = len(products)
    page = products[offset : offset + limit]
    return ProductList(items=page, total=total, limit=limit, offset=offset)


def put_product(product: Product) -> Product:
    """Upsert con id explícito (idempotente). Usado por el cargador de datos (seed)."""
    get_table().put_item(Item=_item_for(product))
    _write_stock_items(product)
    return product


def update_product(product_id: str, data: ProductUpdate) -> Product | None:
    current = get_product(product_id)
    if not current:
        return None
    updates = data.model_dump(exclude_unset=True)
    merged = current.model_dump()
    merged.update(updates)
    product = Product(**merged)
    get_table().put_item(Item=_item_for(product))
    _write_stock_items(product)
    return product


def delete_product(product_id: str) -> bool:
    """Soft delete: marca is_active=False."""
    current = get_product(product_id)
    if not current:
        return False
    current.is_active = False
    get_table().put_item(Item=_item_for(current))
    return True
