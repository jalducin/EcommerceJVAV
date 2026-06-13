"""Tests del núcleo de integración (Sprint 1): mapeo de IDs, framework, vault, mock."""

from __future__ import annotations

import pytest

# ── Mapeo de IDs externo <-> canónico ────────────────────────────────────────


def test_mapeo_bidireccional(dynamo):
    from backend.integrations import mapping
    from backend.integrations.canonical import EntityType

    mapping.set_mapping(
        "shopify", EntityType.PRODUCT, "gid://shopify/Product/123", "prod-abc"
    )

    assert (
        mapping.get_canonical_id(
            "shopify", EntityType.PRODUCT, "gid://shopify/Product/123"
        )
        == "prod-abc"
    )
    assert (
        mapping.get_external_id("shopify", EntityType.PRODUCT, "prod-abc")
        == "gid://shopify/Product/123"
    )


def test_mapeo_inexistente_devuelve_none(dynamo):
    from backend.integrations import mapping
    from backend.integrations.canonical import EntityType

    assert mapping.get_canonical_id("shopify", EntityType.ORDER, "nope") is None
    assert mapping.get_external_id("shopify", EntityType.ORDER, "nope") is None


def test_mapeo_aislado_por_conector(dynamo):
    from backend.integrations import mapping
    from backend.integrations.canonical import EntityType

    mapping.set_mapping("shopify", EntityType.PRODUCT, "X", "canon-1")
    mapping.set_mapping("woocommerce", EntityType.PRODUCT, "X", "canon-2")
    assert mapping.get_canonical_id("shopify", EntityType.PRODUCT, "X") == "canon-1"
    assert mapping.get_canonical_id("woocommerce", EntityType.PRODUCT, "X") == "canon-2"


# ── Framework: registro y capacidades ────────────────────────────────────────


@pytest.fixture
def fresh_registry():
    from backend.integrations import connector

    connector.clear()
    yield connector
    connector.clear()


def test_registro_y_capacidades(fresh_registry):
    from backend.integrations.connector import Capability
    from backend.integrations.connectors.mock import MockConnector

    fresh_registry.register(MockConnector())
    assert fresh_registry.get("mock") is not None
    assert fresh_registry.get("mock").supports(Capability.CATALOG)
    assert not fresh_registry.get("mock").supports(Capability.PAYMENTS)
    assert len(fresh_registry.with_capability(Capability.INVENTORY)) == 1
    assert len(fresh_registry.with_capability(Capability.PAYMENTS)) == 0


def test_capacidad_no_soportada_se_rechaza(fresh_registry):
    from backend.integrations.connectors.mock import MockConnector

    mock = MockConnector()
    mock.capabilities = set()  # sin capacidades
    with pytest.raises(RuntimeError):
        mock.push_inventory("prod-1", "SKU", 5)


# ── Conector mock: traducción a canónico ─────────────────────────────────────


def test_mock_traduce_pedido_a_canonico(fresh_registry):
    from backend.integrations.connectors.mock import MockConnector

    mock = MockConnector()
    external = {
        "id": 9001,
        "status": "paid",
        "total": 1998.0,
        "currency": "MXN",
        "lines": [
            {"sku": "RUN-42", "name": "Tenis", "unit_price": 999.0, "quantity": 2}
        ],
    }
    order = mock.to_canonical_order(external, canonical_id="ord-xyz")
    assert order.channel == "mock"
    assert order.external_id == "9001"
    assert order.canonical_id == "ord-xyz"
    assert len(order.lines) == 1
    assert order.lines[0].sku == "RUN-42"


# ── Vault de credenciales (Secrets Manager via moto) ──────────────────────────


def test_vault_guarda_y_lee(aws_credentials):
    from moto import mock_aws

    with mock_aws():
        from backend.integrations import vault

        assert vault.get_credentials("shopify") is None
        vault.put_credentials("shopify", {"access_token": "shpat_123"})
        creds = vault.get_credentials("shopify")
        assert creds == {"access_token": "shpat_123"}

        # Idempotente: actualizar sobre un secreto existente
        vault.put_credentials("shopify", {"access_token": "shpat_456"})
        assert vault.get_credentials("shopify")["access_token"] == "shpat_456"
