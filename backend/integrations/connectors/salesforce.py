"""Conector de Salesforce (CRM). Sprint 5 — DEUDA TÉCNICA (diferido).

Requiere org de Salesforce (Developer Edition limitada); no ejecutable en tier 0.
El mapeo a contacto sí se prueba; la verificación en vivo queda diferida.
"""

from __future__ import annotations

from backend.integrations.connectors.crm_base import CrmConnector


class SalesforceConnector(CrmConnector):
    name = "salesforce"
    deferred = True
