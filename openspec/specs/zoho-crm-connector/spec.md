# zoho-crm-connector Specification

## Purpose
TBD - created by archiving change crm-erp-inventory. Update Purpose after archive.
## Requirements
### Requirement: Adapter de Zoho CRM sobre el connector framework

El conector de Zoho CRM SHALL implementar la interfaz de adapter y declarar la capacidad `clientes` (sync
de Contactos/Leads) y, donde aplique, `pedidos` como Deals. La autenticación SHALL usar OAuth 2.0 con
tokens en el vault. Es ejecutable con la edición **free** de Zoho CRM.

#### Scenario: Cliente canónico sincronizado en Zoho

- **WHEN** se crea o actualiza un cliente canónico marcado para Zoho CRM
- **THEN** el adapter crea/actualiza el Contacto vía API resolviendo el mapeo de IDs
- **AND** la operación es idempotente (no duplica)

