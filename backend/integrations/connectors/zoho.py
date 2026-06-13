"""Conector de Zoho CRM. Sprint 5 — ejecutable con la edición free."""

from __future__ import annotations

from backend.integrations.connectors.crm_base import CrmConnector


class ZohoCrmConnector(CrmConnector):
    name = "zoho"
