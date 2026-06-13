"""Sincronización de inventario entrante desde un ERP/IMS, respetando la fuente de verdad.

Si el conector ERP/IMS es la fuente de verdad de `inventory`, sus niveles sobrescriben el
inventario canónico (items STOCK#). Si no lo es, NO se aplica (no se sobrescribe la fuente).
"""

from __future__ import annotations

from backend.db import keys
from backend.db.dynamo import get_table
from backend.integrations import source_of_truth
from backend.integrations.connectors.erp_base import ErpConnector


def apply_external_inventory(
    connector: ErpConnector, product_id: str, sku: str, available: int
) -> bool:
    """Aplica un nivel del ERP/IMS al inventario canónico si es la fuente de verdad.

    Devuelve True si se aplicó; False si el conector no es la fuente de `inventory`.
    """
    if not source_of_truth.is_source("inventory", connector.name):
        return False
    get_table().update_item(
        Key={"PK": keys.product_pk(product_id), "SK": keys.stock_sk(sku)},
        UpdateExpression="SET stock = :n",
        ExpressionAttributeValues={":n": int(available)},
    )
    return True
