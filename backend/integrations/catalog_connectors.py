"""Catálogo de todos los conectores disponibles (para la vista admin de integraciones).

Enumera los conectores implementados con su categoría, capacidades y si están
diferidos (deuda técnica, no ejecutables en tier 0).
"""

from __future__ import annotations

from backend.integrations.connectors.amazon import AmazonConnector
from backend.integrations.connectors.clip import ClipConnector
from backend.integrations.connectors.conekta import ConektaConnector
from backend.integrations.connectors.google_merchant import GoogleMerchantConnector
from backend.integrations.connectors.hubspot import HubSpotConnector
from backend.integrations.connectors.inventory_ims import InventoryImsConnector
from backend.integrations.connectors.lightspeed import LightspeedConnector
from backend.integrations.connectors.mercadolibre import MercadoLibreConnector
from backend.integrations.connectors.meta import MetaConnector
from backend.integrations.connectors.netsuite import NetSuiteConnector
from backend.integrations.connectors.odoo import OdooConnector
from backend.integrations.connectors.salesforce import SalesforceConnector
from backend.integrations.connectors.shopify import ShopifyConnector
from backend.integrations.connectors.square import SquareConnector
from backend.integrations.connectors.stripe_terminal import StripeTerminalConnector
from backend.integrations.connectors.tiktok import TikTokShopConnector
from backend.integrations.connectors.woocommerce import WooCommerceConnector
from backend.integrations.connectors.zoho import ZohoCrmConnector

# (categoría, clase)
_CONNECTORS = [
    ("canal", ShopifyConnector),
    ("canal", WooCommerceConnector),
    ("marketplace", AmazonConnector),
    ("marketplace", MercadoLibreConnector),
    ("social", MetaConnector),
    ("social", TikTokShopConnector),
    ("feed", GoogleMerchantConnector),
    ("crm", HubSpotConnector),
    ("crm", ZohoCrmConnector),
    ("crm", SalesforceConnector),
    ("erp", OdooConnector),
    ("erp", NetSuiteConnector),
    ("inventario", InventoryImsConnector),
    ("pos", SquareConnector),
    ("pos", LightspeedConnector),
    ("pago", StripeTerminalConnector),
    ("pago", ClipConnector),
    ("pago", ConektaConnector),
]


def all_connectors() -> list[dict]:
    """Metadatos de todos los conectores para la vista de integraciones del admin."""
    out = []
    for category, cls in _CONNECTORS:
        c = cls()
        out.append(
            {
                "name": c.name,
                "category": category,
                "capabilities": sorted(cap.value for cap in c.capabilities),
                "deferred": c.deferred,
                "status": "deuda_tecnica" if c.deferred else "disponible",
            }
        )
    return out
