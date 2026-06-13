# hubspot-connector Specification

## Purpose
TBD - created by archiving change crm-erp-inventory. Update Purpose after archive.
## Requirements
### Requirement: Adapter de HubSpot sobre el connector framework

El conector de HubSpot SHALL implementar la interfaz de adapter y declarar la capacidad `clientes` (sync
de Contactos) y, donde aplique, `pedidos` como Deals. La autenticación SHALL usar OAuth/Private App token
en el vault. Es ejecutable con la edición **free** de HubSpot.

#### Scenario: Cliente canónico sincronizado como Contacto de HubSpot

- **WHEN** se crea o actualiza un cliente canónico marcado para HubSpot
- **THEN** el adapter crea/actualiza el Contacto vía API resolviendo el mapeo de IDs
- **AND** la operación es idempotente

#### Scenario: Pedido reflejado como Deal (cuando aplique)

- **WHEN** un pedido canónico debe reflejarse como Deal en HubSpot
- **THEN** el adapter crea/actualiza el Deal asociado al Contacto
- **AND** evita duplicados por el mapeo de IDs

