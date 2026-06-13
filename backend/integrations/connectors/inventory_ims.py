"""Conector de inventario multialmacén (Cin7/Skubana). Sprint 5 — requiere cuenta del proveedor."""

from __future__ import annotations

from backend.integrations.connectors.erp_base import ErpConnector


class InventoryImsConnector(ErpConnector):
    name = "inventory_ims"
