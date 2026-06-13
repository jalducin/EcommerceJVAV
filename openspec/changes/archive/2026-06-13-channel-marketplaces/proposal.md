## Why

Amazon y MercadoLibre son los marketplaces clave (Amazon global, MercadoLibre LATAM). Aportan volumen
pero con APIs más complejas (OAuth/LWA, rate limits estrictos, modelos de listing y fulfillment propios).
Se abordan tras validar el framework con Shopify/Woo. Sprint 3 del roadmap.

## What Changes

- **Adapter de Amazon SP-API**: autenticación LWA/OAuth, listings, inventario (FBA/FBM), pedidos y
  notificaciones; manejo de los rate limits y modelos de feed de Amazon.
- **Adapter de MercadoLibre**: OAuth, publicaciones, inventario, pedidos y notificaciones (topics).
- Sync de inventario y publicación de listings desde el catálogo canónico; ingesta de pedidos al hub
  unificado; reconciliación periódica.

## Capabilities

### New Capabilities
- `amazon-spapi-connector`: adapter de Amazon SP-API (listings, inventario, pedidos, notificaciones).
- `mercadolibre-connector`: adapter de MercadoLibre (publicaciones, inventario, pedidos, notificaciones).

### Modified Capabilities
<!-- Usa las capabilities del Sprint 1. -->

## Impact

- **Backend**: `backend/integrations/amazon/` y `backend/integrations/mercadolibre/` (auth, mapeo de
  listings, manejo de rate limits y notificaciones).
- **Infra**: secretos OAuth/LWA, colas dedicadas con throttling por proveedor, suscripción a
  notificaciones (SQS/SNS de cada marketplace donde aplique).
- **Tests**: contra MercadoLibre test users (gratis); Amazon SP-API requiere cuenta de vendedor y
  aprobación — specs sí, ejecución solo con acceso.
- **Docs**: sección por conector; particularidades de rate limit y feeds.
- **Dependencia**: requiere `integration-platform-core` (Sprint 1).
- **Acceso**: MercadoLibre tiene sandbox gratis; **Amazon SP-API requiere cuenta pagada/aprobación**.
