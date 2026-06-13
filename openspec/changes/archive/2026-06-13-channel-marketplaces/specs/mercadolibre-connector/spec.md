## ADDED Requirements

### Requirement: Adapter de MercadoLibre sobre el connector framework

El conector de MercadoLibre SHALL implementar la interfaz de adapter y declarar las capacidades
`catalogo`, `inventario` y `pedidos`. La autenticación SHALL usar OAuth 2.0 con refresh token en el vault.
Es ejecutable con **test users** gratuitos de MercadoLibre.

#### Scenario: Conector autenticado con OAuth

- **WHEN** se completa el flujo OAuth y el refresh token queda en el vault
- **THEN** el adapter obtiene y refresca el access token automáticamente
- **AND** queda registrado con sus capacidades declaradas

### Requirement: Publicaciones e inventario hacia MercadoLibre

El conector SHALL crear/actualizar publicaciones (items) y su inventario desde el catálogo canónico,
resolviendo el id externo (MLM/MLA…) vía el mapeo de IDs y respetando el rate limit a través del motor de
sincronización.

#### Scenario: Publicación creada y mapeada

- **WHEN** un producto canónico se marca para publicarse en MercadoLibre
- **THEN** el adapter crea la publicación y registra el mapeo de IDs
- **AND** las actualizaciones de stock posteriores usan ese id externo

### Requirement: Ingesta de pedidos de MercadoLibre al hub unificado

Los pedidos SHALL ingresar al hub unificado mediante las notificaciones (topics) de MercadoLibre y/o pull
de la Orders API, de forma idempotente y deduplicada por el mapeo de IDs.

#### Scenario: Notificación de pedido crea pedido canónico

- **WHEN** llega una notificación de orden de MercadoLibre
- **THEN** se crea (o actualiza) un Pedido canónico con canal de origen `mercadolibre`
- **AND** el inventario unificado se descuenta una sola vez (idempotente)
