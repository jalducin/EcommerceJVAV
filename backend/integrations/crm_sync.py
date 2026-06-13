"""Sincronización de clientes hacia un CRM (idempotente, deduplicada por mapeo de IDs).

El CRM es destino para la entidad `customers` cuando el canónico es su fuente de verdad.
Reingresar el mismo cliente no crea un contacto duplicado (mismo id externo mapeado).
"""

from __future__ import annotations

from backend.integrations import mapping, source_of_truth
from backend.integrations.canonical import CanonicalCustomer, EntityType
from backend.integrations.connectors.crm_base import CrmConnector


class NotSourceOfTruthError(Exception):
    """El canónico no es la fuente de verdad de `customers`: no se debe empujar al CRM."""


def sync_customer(connector: CrmConnector, customer: CanonicalCustomer) -> str:
    """Crea/actualiza el contacto en el CRM. Devuelve su id externo. Idempotente."""
    # El push canónico->CRM solo procede si el canónico manda en customers.
    if not source_of_truth.is_source("customers", "canonical"):
        raise NotSourceOfTruthError(
            "customers no tiene al canónico como fuente de verdad"
        )

    existing = mapping.get_external_id(
        connector.name, EntityType.CUSTOMER, customer.canonical_id
    )
    payload = connector.to_contact(customer)

    if existing:
        connector.push_contact(payload)  # actualiza (idempotente), no duplica
        return existing

    external_id = connector.push_contact(payload)
    mapping.set_mapping(
        connector.name, EntityType.CUSTOMER, external_id, customer.canonical_id
    )
    return external_id
