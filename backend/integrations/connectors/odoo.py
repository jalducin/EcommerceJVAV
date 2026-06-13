"""Conector de Odoo (ERP, JSON-RPC). Sprint 5 — ejecutable con Odoo community/local."""

from __future__ import annotations

from backend.integrations.connectors.erp_base import ErpConnector


class OdooConnector(ErpConnector):
    name = "odoo"
