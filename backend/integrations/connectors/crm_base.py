"""Base de conectores CRM (sync de clientes/contactos).

Capacidad CUSTOMERS. `to_contact` mapea el cliente canónico al payload del CRM;
`push_contact` lo envía. Sin credenciales reales (tier 0 / local) opera en modo
simulado devolviendo un id externo determinista; con credenciales haría el POST real.
"""

from __future__ import annotations

from backend.integrations.canonical import CanonicalCustomer
from backend.integrations.connector import Capability, ConnectorBase


class CrmConnector(ConnectorBase):
    capabilities = {Capability.CUSTOMERS}

    def to_contact(self, customer: CanonicalCustomer) -> dict:
        """Mapeo genérico cliente canónico -> contacto CRM (subclases pueden afinar)."""
        return {"email": customer.email, "name": customer.full_name}

    def push_contact(self, payload: dict) -> str:
        """Crea/actualiza el contacto en el CRM y devuelve su id externo.

        Modo simulado (sin credenciales): id determinista a partir del email.
        """
        local = payload["email"].split("@")[0]
        return f"{self.name}-{local}"
