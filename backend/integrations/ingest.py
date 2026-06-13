"""Ingesta de pedidos de canales al hub unificado (idempotente).

Deduplica por el mapeo de IDs: un pedido externo -> un único pedido canónico.
Refleja la venta en el inventario unificado (el pedido ya ocurrió en el canal).
"""

from __future__ import annotations

import uuid

from backend.integrations import channel_orders, inventory, mapping
from backend.integrations.canonical import CanonicalOrder, EntityType
from backend.integrations.connectors.channel_base import ChannelConnector


def ingest_order(connector: ChannelConnector, payload: dict) -> CanonicalOrder:
    """Crea (o devuelve) el pedido canónico para un pedido externo. Idempotente."""
    external_id = connector.external_order_id(payload)

    existing_id = mapping.get_canonical_id(
        connector.name, EntityType.ORDER, external_id
    )
    if existing_id:
        order = channel_orders.get_order(existing_id)
        if order:
            return order  # ya ingerido: no duplica

    canonical_id = str(uuid.uuid4())
    order = connector.to_canonical_order(payload, canonical_id)
    channel_orders.save_order(order)
    mapping.set_mapping(connector.name, EntityType.ORDER, external_id, canonical_id)

    # Reflejar inventario por línea (sku -> producto del catálogo canónico).
    for line in order.lines:
        product_id = inventory.find_product_id_by_sku(line.sku)
        if product_id:
            inventory.reflect_sale(product_id, line.sku, line.quantity)

    return order
