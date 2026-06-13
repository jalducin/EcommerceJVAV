"""Framework de conectores: interfaz de adapter, capacidades y registro.

Cada integración (canal de venta, CRM, POS) implementa `ConnectorBase` declarando
sus capacidades. El núcleo solo invoca capacidades declaradas. Añadir un conector =
registrar un adapter; no se toca el núcleo.
"""

from __future__ import annotations

from abc import ABC
from enum import Enum


class Capability(str, Enum):
    CATALOG = "catalog"
    INVENTORY = "inventory"
    ORDERS = "orders"
    CUSTOMERS = "customers"
    PAYMENTS = "payments"
    FULFILLMENT = "fulfillment"


class SyncDirection(str, Enum):
    INBOUND = "inbound"  # del proveedor hacia el canónico
    OUTBOUND = "outbound"  # del canónico hacia el proveedor
    BIDIRECTIONAL = "bidirectional"


class ConnectorBase(ABC):
    """Base de todos los adapters. Subclases definen `name` y `capabilities`."""

    name: str = "base"
    capabilities: set[Capability] = set()
    # Deuda técnica: conector specced/codificado pero no ejecutable en tier 0
    # (requiere cuenta pagada/aprobación). Su verificación en vivo queda diferida.
    deferred: bool = False

    def supports(self, capability: Capability) -> bool:
        return capability in self.capabilities


# --- Registro de conectores habilitados ----------------------------------

_registry: dict[str, ConnectorBase] = {}


def register(connector: ConnectorBase) -> None:
    _registry[connector.name] = connector


def unregister(name: str) -> None:
    _registry.pop(name, None)


def get(name: str) -> ConnectorBase | None:
    return _registry.get(name)


def enabled() -> list[ConnectorBase]:
    return list(_registry.values())


def with_capability(capability: Capability) -> list[ConnectorBase]:
    return [c for c in _registry.values() if c.supports(capability)]


def clear() -> None:
    _registry.clear()
