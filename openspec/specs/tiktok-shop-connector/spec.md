# tiktok-shop-connector Specification

## Purpose
TBD - created by archiving change channel-social-google. Update Purpose after archive.
## Requirements
### Requirement: Adapter de TikTok Shop sobre el connector framework

El conector de TikTok Shop SHALL implementar la interfaz de adapter y declarar las capacidades `catalogo`,
`inventario` y `pedidos`. La autenticación SHALL usar el flujo OAuth de TikTok Shop con tokens en el vault.

#### Scenario: Conector autenticado y registrado

- **WHEN** se completa el OAuth de TikTok Shop y los tokens quedan en el vault
- **THEN** el adapter queda registrado con sus capacidades
- **AND** refresca el token automáticamente al expirar

### Requirement: Catálogo, inventario y pedidos con TikTok Shop

El conector SHALL publicar catálogo/inventario canónicos en TikTok Shop e ingresar sus pedidos al hub
unificado (webhooks/notificaciones + pull), de forma idempotente y deduplicada por el mapeo de IDs,
respetando el rate limit a través del motor de sincronización.

#### Scenario: Pedido de TikTok Shop ingresa al hub

- **WHEN** llega un pedido de TikTok Shop
- **THEN** se crea (o actualiza) un Pedido canónico con canal de origen `tiktok`
- **AND** el inventario unificado se descuenta una sola vez (idempotente)

