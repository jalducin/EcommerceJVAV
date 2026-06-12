"""Fundación DynamoDB single-table para MetalShop serverless.

Una sola tabla con clave compuesta (PK, SK) y tres índices secundarios globales:
- GSI1: lookup de usuario por email (GSI1PK=EMAIL#<email>).
- GSI2: listado de productos por categoría (GSI2PK=CAT#<categoria>).
- GSI3: pedidos (todos / por estado) para administración (GSI3PK=ORDERS).

El cliente usa boto3 (sync). En tests se mockea con moto; en local puede apuntar a
DynamoDB Local vía DYNAMODB_ENDPOINT_URL; en AWS usa la región configurada.
"""

from __future__ import annotations

import boto3

from backend.config import settings

# Definición de índices secundarios globales (clave de partición + ordenamiento).
GSI_DEFS = [
    ("GSI1", "GSI1PK", "GSI1SK"),
    ("GSI2", "GSI2PK", "GSI2SK"),
    ("GSI3", "GSI3PK", "GSI3SK"),
]


def _resource_kwargs() -> dict:
    kwargs: dict = {"region_name": settings.AWS_REGION}
    if settings.DYNAMODB_ENDPOINT_URL:
        kwargs["endpoint_url"] = settings.DYNAMODB_ENDPOINT_URL
    return kwargs


def get_resource():
    """Devuelve un recurso DynamoDB de boto3 (respeta endpoint local y región)."""
    return boto3.resource("dynamodb", **_resource_kwargs())


def get_table():
    """Devuelve el objeto Table de la tabla única configurada."""
    return get_resource().Table(settings.DYNAMODB_TABLE)


def get_client():
    """Cliente DynamoDB de bajo nivel (para transact_write_items con formato tipado)."""
    return boto3.client("dynamodb", **_resource_kwargs())


def create_table(table_name: str | None = None) -> None:
    """Crea la tabla single-table con sus GSIs si no existe (idempotente).

    Pensado para tests (moto), DynamoDB Local y aprovisionamiento de un entorno dev.
    En producción la tabla la define la IaC (SAM/CloudFormation).
    """
    name = table_name or settings.DYNAMODB_TABLE
    client = boto3.client("dynamodb", **_resource_kwargs())

    existing = client.list_tables().get("TableNames", [])
    if name in existing:
        return

    attribute_names = ["PK", "SK"]
    for _, pk, sk in GSI_DEFS:
        attribute_names.extend([pk, sk])

    client.create_table(
        TableName=name,
        BillingMode="PAY_PER_REQUEST",
        KeySchema=[
            {"AttributeName": "PK", "KeyType": "HASH"},
            {"AttributeName": "SK", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": attr, "AttributeType": "S"} for attr in attribute_names
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": index,
                "KeySchema": [
                    {"AttributeName": pk, "KeyType": "HASH"},
                    {"AttributeName": sk, "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            }
            for index, pk, sk in GSI_DEFS
        ],
    )
    client.get_waiter("table_exists").wait(TableName=name)
