## ADDED Requirements

### Requirement: Adapter de Shopify sobre el connector framework

El conector de Shopify SHALL implementar la interfaz de adapter del núcleo y declarar las capacidades
`catalogo`, `inventario`, `pedidos` y `fulfillment`. La autenticación SHALL usar el token/OAuth de la
tienda almacenado en el vault de credenciales; nunca credenciales en código.

#### Scenario: Conector registrado y autenticado

- **WHEN** se habilita el conector de Shopify para una tienda con su token en el vault
- **THEN** el adapter queda registrado con sus capacidades declaradas
- **AND** sus llamadas a la Admin API usan el token resuelto desde el vault

### Requirement: Publicación de catálogo e inventario hacia Shopify

El conector SHALL publicar y actualizar productos/variantes y niveles de inventario canónicos en Shopify,
resolviendo el id de Shopify vía el mapeo de IDs (creándolo si no existe). La propagación de stock SHALL
pasar por el motor de sincronización (async, idempotente, con rate limiting de la API de Shopify).

#### Scenario: Cambio de stock canónico se refleja en Shopify

- **WHEN** cambia el nivel de inventario de una variante publicada en Shopify
- **THEN** el motor encola la actualización y el adapter actualiza el stock en Shopify
- **AND** respeta el rate limit de la Admin API (difiere ante 429, no descarta)

### Requirement: Ingesta de pedidos de Shopify al hub unificado

Los pedidos creados en Shopify SHALL ingresar al hub de pedidos unificado vía webhook (`orders/create`),
con validación de firma HMAC, y SHALL reconciliarse por pull como respaldo. La ingesta SHALL ser
idempotente y deduplicada por el mapeo de IDs.

#### Scenario: Webhook de pedido de Shopify crea pedido canónico

- **WHEN** llega un webhook `orders/create` de Shopify con HMAC válido
- **THEN** se crea un Pedido canónico con canal de origen `shopify` y su id externo
- **AND** se descuenta el inventario unificado una sola vez (idempotente)

#### Scenario: Reconciliación por pull no duplica

- **WHEN** la reconciliación periódica trae un pedido de Shopify ya ingresado por webhook
- **THEN** no se crea un duplicado canónico
- **AND** se actualiza el pedido existente si cambió
