## Why

Shopify y WooCommerce son los canales e-commerce más accesibles (REST + sandbox/dev gratis) y los
primeros conectores reales sobre el núcleo de integración. Validan el framework de adapters con
proveedores reales antes de abordar marketplaces y POS más complejos. Sprint 2 del roadmap.

## What Changes

- Se añade un **adapter de Shopify** (Admin API) y un **adapter de WooCommerce** (REST API) sobre el
  connector framework del Sprint 1.
- **Sync de catálogo e inventario** (push): los productos/variantes y niveles de stock canónicos se
  publican y actualizan en cada tienda conectada.
- **Ingesta de pedidos**: pedidos creados en Shopify/Woo entran al hub de pedidos unificado vía webhooks
  (y reconciliación por pull como respaldo).
- **Estados de fulfillment**: cambios de estado se reflejan entre el canónico y el canal.
- Autenticación por tienda vía el vault de credenciales (API key/secret o OAuth de Shopify).

## Capabilities

### New Capabilities
- `shopify-connector`: adapter de Shopify (catálogo, inventario, pedidos, fulfillment) sobre el framework.
- `woocommerce-connector`: adapter de WooCommerce REST (catálogo, inventario, pedidos, fulfillment).

### Modified Capabilities
<!-- Usa (no modifica) las capabilities del Sprint 1: connector-framework, sync-engine, unified-inventory,
     unified-orders, webhook-ingestion. -->

## Impact

- **Backend**: `backend/integrations/shopify/` y `backend/integrations/woocommerce/` (adapters + mapeo);
  handlers de webhook por proveedor.
- **Infra**: rutas de webhook y secretos por tienda; rate limits propios de cada API.
- **Tests**: contra Shopify dev store y WooCommerce local (o respuestas grabadas/mock); sync de inventario
  y anti-sobreventa con dos canales.
- **Docs**: sección por conector en `docs/integrations-standards.md`.
- **Dependencia**: requiere `integration-platform-core` (Sprint 1).
- **Sandbox**: Shopify development store y WooCommerce local son gratuitos para practicar.
