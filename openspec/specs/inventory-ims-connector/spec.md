# inventory-ims-connector Specification

## Purpose
TBD - created by archiving change crm-erp-inventory. Update Purpose after archive.
## Requirements
### Requirement: Adapter de inventario multialmacén (Cin7/Skubana)

El conector de IMS SHALL implementar la interfaz de adapter y declarar la capacidad `inventario`,
soportando **niveles de stock por almacén**. La autenticación SHALL usar las credenciales del proveedor
(Cin7/Skubana) en el vault. Requiere cuenta del proveedor.

#### Scenario: Stock por almacén sincronizado al inventario unificado

- **WHEN** el IMS reporta niveles por almacén
- **THEN** el adapter los aplica al inventario unificado conservando la dimensión de almacén
- **AND** la agregación disponible para venta respeta las reglas de fuente de verdad

#### Scenario: Cambio de stock unificado propagado al IMS (cuando el canónico manda)

- **WHEN** el inventario unificado es fuente de verdad y cambia un nivel
- **THEN** el adapter propaga el cambio al IMS de forma idempotente
- **AND** respeta el rate limit del proveedor

