## ADDED Requirements

### Requirement: Adapter de Meta Commerce sobre el connector framework

El conector de Meta SHALL implementar la interfaz de adapter y declarar la capacidad `catalogo` (feed de
productos para Facebook/Instagram Shop) y, donde la plataforma lo permita, `pedidos`. La autenticación
SHALL usar OAuth de Meta (Graph API) con tokens en el vault.

#### Scenario: Catálogo canónico publicado como feed de Meta

- **WHEN** se sincroniza el catálogo hacia un catálogo de Meta Commerce
- **THEN** el adapter publica/actualiza los productos vía Graph API (o feed) resolviendo el mapeo de IDs
- **AND** los cambios de inventario/precio se propagan por el motor de sincronización

### Requirement: Ingesta de pedidos sociales (cuando aplique)

Cuando el canal soporte checkout nativo, los pedidos SHALL ingresar al hub unificado de forma idempotente
y deduplicada por el mapeo de IDs, conservando el canal de origen `meta`.

#### Scenario: Pedido de Instagram Shop ingresa al hub

- **WHEN** llega un pedido desde Instagram Shop (donde el checkout nativo esté disponible)
- **THEN** se crea un Pedido canónico con canal de origen `meta`
- **AND** el inventario unificado se descuenta una sola vez
