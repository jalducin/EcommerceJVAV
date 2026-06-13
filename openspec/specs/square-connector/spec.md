# square-connector Specification

## Purpose
TBD - created by archiving change pos-payments. Update Purpose after archive.
## Requirements
### Requirement: Adapter de Square sobre el connector framework

El conector de Square SHALL implementar la interfaz de adapter y declarar las capacidades `catalogo`,
`inventario`, `pedidos` y `pagos`. La autenticación SHALL usar OAuth/access token de Square en el vault.
Es ejecutable con el **sandbox** gratuito de Square.

#### Scenario: Venta presencial ingresa al hub unificado

- **WHEN** se registra una venta en Square (POS)
- **THEN** se crea un Pedido canónico con canal de origen `square` y su id externo
- **AND** el inventario unificado se descuenta una sola vez (idempotente)

#### Scenario: Catálogo e inventario sincronizados con Square

- **WHEN** cambia el catálogo o el stock canónico de un ítem vendido en tienda
- **THEN** el adapter sincroniza el catálogo/inventario con Square vía el motor de sincronización
- **AND** respeta el rate limit de la API

