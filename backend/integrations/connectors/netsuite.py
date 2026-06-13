"""Conector de NetSuite (ERP). Sprint 5 — DEUDA TÉCNICA (diferido).

Requiere licencia/cuenta NetSuite (TBA OAuth); no ejecutable en tier 0. El mapeo de
niveles sí se prueba; la verificación en vivo queda diferida.
"""

from __future__ import annotations

from backend.integrations.connectors.erp_base import ErpConnector


class NetSuiteConnector(ErpConnector):
    name = "netsuite"
    deferred = True
