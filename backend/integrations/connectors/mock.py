"""Conector de referencia (mock) para validar el framework sin un proveedor real.

Implementa la interfaz declarando capacidades y registra las operaciones recibidas,
de modo que los tests verifiquen el framework (registro, capacidades, mapeo, sync).
"""

from __future__ import annotations

from backend.integrations.canonical import (
    CanonicalOrder,
    CanonicalOrderLine,
    EntityType,
)
from backend.integrations.connector import Capability, ConnectorBase


class MockConnector(ConnectorBase):
    name = "mock"
    capabilities = {Capability.CATALOG, Capability.INVENTORY, Capability.ORDERS}

    def __init__(self) -> None:
        # Registro de efectos para inspección en tests.
        self.pushed_inventory: list[tuple[str, str, int]] = []
        self.authenticated = False

    def authenticate(self) -> bool:
        self.authenticated = True
        return True

    def push_inventory(
        self, canonical_product_id: str, sku: str, available: int
    ) -> None:
        if not self.supports(Capability.INVENTORY):
            raise RuntimeError("Capacidad inventory no soportada")
        self.pushed_inventory.append((canonical_product_id, sku, available))

    def to_canonical_order(self, external: dict, canonical_id: str) -> CanonicalOrder:
        """Traduce un pedido del proveedor (dict) al modelo canónico."""
        lines = [
            CanonicalOrderLine(
                sku=line.get("sku", "-"),
                name=line.get("name", ""),
                unit_price=float(line.get("unit_price", 0)),
                quantity=int(line.get("quantity", 1)),
            )
            for line in external.get("lines", [])
        ]
        return CanonicalOrder(
            canonical_id=canonical_id,
            channel=self.name,
            external_id=str(external["id"]),
            status=external.get("status", "pending"),
            lines=lines,
            total=float(external.get("total", 0)),
            currency=external.get("currency", "MXN"),
            customer_email=external.get("customer_email"),
        )

    # Tipo de entidad principal que ingesta este conector.
    order_entity = EntityType.ORDER
