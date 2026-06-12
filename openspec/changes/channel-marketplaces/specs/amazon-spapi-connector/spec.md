## ADDED Requirements

### Requirement: Adapter de Amazon SP-API sobre el connector framework

El conector de Amazon SHALL implementar la interfaz de adapter y declarar las capacidades `catalogo`,
`inventario` y `pedidos`. La autenticación SHALL usar el flujo LWA (Login with Amazon) con refresh token
en el vault de credenciales. La implementación SHALL marcarse como **deuda técnica diferida**: requiere
cuenta de vendedor profesional y aprobación de la app (no ejecutable en tier 0).

#### Scenario: Conector configurado con LWA

- **WHEN** se configura el conector con las credenciales LWA en el vault
- **THEN** el adapter obtiene y refresca el access token automáticamente
- **AND** queda registrado con sus capacidades declaradas

### Requirement: Listings e inventario hacia Amazon

El conector SHALL publicar/actualizar listings e inventario (FBA/FBM) desde el catálogo canónico mediante
los feeds/APIs de SP-API, resolviendo el id externo (ASIN/SKU) vía el mapeo de IDs y respetando los rate
limits estrictos de SP-API a través del motor de sincronización.

#### Scenario: Actualización de inventario respeta rate limits

- **WHEN** se propaga un cambio de stock a Amazon
- **THEN** el adapter envía la actualización vía SP-API
- **AND** ante throttling difiere y reintenta con backoff sin descartar el trabajo

### Requirement: Ingesta de pedidos de Amazon al hub unificado

Los pedidos de Amazon SHALL ingresar al hub unificado mediante las notificaciones de SP-API
(EventBridge/SQS de Amazon) y/o pull de la Orders API, de forma idempotente y deduplicada por el mapeo de IDs.

#### Scenario: Pedido de Amazon ingresa una sola vez

- **WHEN** llega una notificación de pedido de Amazon ya ingresado por pull
- **THEN** no se duplica el pedido canónico
- **AND** se conserva el canal de origen `amazon` y su id externo
