## ADDED Requirements

### Requirement: Adapter de WooCommerce sobre el connector framework

El conector de WooCommerce SHALL implementar la interfaz de adapter y declarar las capacidades
`catalogo`, `inventario`, `pedidos` y `fulfillment`. La autenticación SHALL usar la consumer key/secret de
la tienda almacenadas en el vault de credenciales.

#### Scenario: Conector registrado y autenticado

- **WHEN** se habilita el conector de WooCommerce con su consumer key/secret en el vault
- **THEN** el adapter queda registrado con sus capacidades declaradas
- **AND** sus llamadas a la REST API usan las credenciales resueltas desde el vault

### Requirement: Publicación de catálogo e inventario hacia WooCommerce

El conector SHALL publicar y actualizar productos/variantes y niveles de inventario canónicos en
WooCommerce, resolviendo el id externo vía el mapeo de IDs. La propagación de stock SHALL pasar por el
motor de sincronización (async, idempotente, con rate limiting).

#### Scenario: Producto canónico nuevo se publica en WooCommerce

- **WHEN** un producto canónico se marca para publicarse en una tienda WooCommerce
- **THEN** el adapter lo crea vía REST API y registra el mapeo de IDs
- **AND** las actualizaciones posteriores usan ese id externo

### Requirement: Ingesta de pedidos de WooCommerce al hub unificado

Los pedidos de WooCommerce SHALL ingresar al hub unificado vía webhook con validación de firma, y
reconciliarse por pull como respaldo. La ingesta SHALL ser idempotente y deduplicada por el mapeo de IDs.

#### Scenario: Webhook de pedido de WooCommerce crea pedido canónico

- **WHEN** llega un webhook de pedido de WooCommerce con firma válida
- **THEN** se crea un Pedido canónico con canal de origen `woocommerce` y su id externo
- **AND** el inventario unificado se descuenta una sola vez
