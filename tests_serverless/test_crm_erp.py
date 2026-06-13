"""Tests de Sprint 5: CRM (clientes), ERP/IMS (inventario) y fuente de verdad."""

from __future__ import annotations

from backend.integrations.canonical import CanonicalCustomer
from backend.integrations.connector import Capability
from backend.integrations.connectors.hubspot import HubSpotConnector
from backend.integrations.connectors.inventory_ims import InventoryImsConnector
from backend.integrations.connectors.netsuite import NetSuiteConnector
from backend.integrations.connectors.odoo import OdooConnector
from backend.integrations.connectors.salesforce import SalesforceConnector
from backend.integrations.connectors.zoho import ZohoCrmConnector


def _seed_producto(dynamo):
    from backend.repositories import product_repo
    from backend.schemas.catalog import ProductCreate, Variant

    product_repo.create_product(
        ProductCreate(
            name="Tenis Runner",
            price=1000.0,
            category="tenis",
            variants=[Variant(sku="RUN-42", attrs={"talla": "42"}, stock=10)],
        )
    )


# ── Capacidades y deuda técnica ───────────────────────────────────────────────


def test_capacidades_crm_erp():
    for crm in (HubSpotConnector(), ZohoCrmConnector(), SalesforceConnector()):
        assert crm.supports(Capability.CUSTOMERS)
        assert not crm.supports(Capability.INVENTORY)
    for erp in (OdooConnector(), InventoryImsConnector(), NetSuiteConnector()):
        assert erp.supports(Capability.INVENTORY)
    # Diferidos
    assert SalesforceConnector().deferred is True
    assert NetSuiteConnector().deferred is True
    assert HubSpotConnector().deferred is False


# ── CRM: sync de clientes idempotente ─────────────────────────────────────────


def test_sync_customer_idempotente(dynamo):
    from backend.integrations import crm_sync, mapping
    from backend.integrations.canonical import EntityType

    conn = HubSpotConnector()
    cliente = CanonicalCustomer(
        canonical_id="cust-1", email="ana@correo.mx", full_name="Ana"
    )
    ext1 = crm_sync.sync_customer(conn, cliente)
    ext2 = crm_sync.sync_customer(conn, cliente)  # mismo cliente

    assert ext1 == ext2  # no duplica
    assert mapping.get_canonical_id("hubspot", EntityType.CUSTOMER, ext1) == "cust-1"


def test_sync_customer_respeta_fuente_de_verdad(dynamo):
    from backend.integrations import crm_sync, source_of_truth

    # Si el CRM (no el canónico) es la fuente de clientes, no se empuja al CRM.
    source_of_truth.set_rule("customers", "hubspot")
    conn = HubSpotConnector()
    cliente = CanonicalCustomer(canonical_id="c2", email="b@correo.mx")
    try:
        crm_sync.sync_customer(conn, cliente)
        assert False, "debió lanzar NotSourceOfTruthError"
    except crm_sync.NotSourceOfTruthError:
        pass


# ── ERP/IMS: inventario entrante respeta la fuente de verdad ──────────────────


def test_inventario_entrante_aplica_si_es_fuente(dynamo):
    from backend.integrations import inventory, inventory_sync, source_of_truth

    _seed_producto(dynamo)
    pid = inventory.find_product_id_by_sku("RUN-42")
    odoo = OdooConnector()

    # Por defecto el canónico es la fuente -> Odoo NO sobrescribe.
    aplicado = inventory_sync.apply_external_inventory(odoo, pid, "RUN-42", 99)
    assert aplicado is False
    assert inventory.get_stock(pid, "RUN-42") == 10

    # Ahora Odoo es la fuente de verdad de inventario -> sí aplica.
    source_of_truth.set_rule("inventory", "odoo")
    aplicado = inventory_sync.apply_external_inventory(odoo, pid, "RUN-42", 99)
    assert aplicado is True
    assert inventory.get_stock(pid, "RUN-42") == 99


def test_normalize_level_erp(dynamo):
    odoo = OdooConnector()
    n = odoo.normalize_level({"item_code": "RUN-42", "qty": 7, "warehouse": "MX1"})
    assert n == {"sku": "RUN-42", "available": 7, "location": "MX1"}
