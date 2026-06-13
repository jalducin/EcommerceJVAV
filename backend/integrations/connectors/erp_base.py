"""Base de conectores ERP/IMS (sync de inventario por almacén).

Capacidad INVENTORY. La dirección por defecto es entrante (el ERP/IMS reporta niveles
que se aplican al inventario unificado cuando es la fuente de verdad de `inventory`).
`read_inventory` devuelve niveles del proveedor; en modo simulado lo provee el caller.
"""

from __future__ import annotations

from backend.integrations.connector import Capability, ConnectorBase, SyncDirection


class ErpConnector(ConnectorBase):
    capabilities = {Capability.INVENTORY}
    inventory_direction = SyncDirection.INBOUND  # del proveedor hacia el canónico

    def normalize_level(self, raw: dict) -> dict:
        """Normaliza un nivel del proveedor a {sku, available, location}."""
        return {
            "sku": raw.get("sku") or raw.get("item_code") or "-",
            "available": int(raw.get("available", raw.get("qty", 0))),
            "location": raw.get("location") or raw.get("warehouse") or "default",
        }
