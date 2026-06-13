"""Conector de HubSpot (CRM). Sprint 5 — ejecutable con la edición free."""

from __future__ import annotations

from backend.integrations.connectors.crm_base import CrmConnector


class HubSpotConnector(CrmConnector):
    name = "hubspot"
