# source-of-truth-rules Specification

## Purpose
TBD - created by archiving change crm-erp-inventory. Update Purpose after archive.
## Requirements
### Requirement: Reglas de fuente de verdad por entidad configurables

El sistema SHALL permitir configurar, **por entidad** (inventario, clientes, pedidos), qué sistema es la
**fuente de verdad** (el núcleo canónico, un ERP/IMS, o un CRM). La sincronización SHALL respetar estas
reglas: el sistema fuente manda y los demás reciben; no se sobrescribe la fuente con datos de un sistema
subordinado.

#### Scenario: ERP como fuente de verdad de inventario

- **WHEN** la configuración define al ERP como fuente de verdad de inventario
- **THEN** los cambios de stock del ERP actualizan el inventario unificado
- **AND** los sistemas subordinados reciben el nivel, sin que estos puedan sobrescribir al ERP

#### Scenario: Conflicto resuelto a favor de la fuente

- **WHEN** dos sistemas reportan valores distintos para la misma entidad
- **THEN** prevalece el valor del sistema definido como fuente de verdad
- **AND** el conflicto queda registrado en la observabilidad

### Requirement: Dirección de sincronización explícita por conector

Cada conector de CRM/ERP/IMS SHALL declarar la **dirección** de sincronización soportada por entidad
(entrante, saliente o bidireccional), y el motor SHALL combinarla con las reglas de fuente de verdad para
decidir qué operaciones ejecutar.

#### Scenario: Conector solo entrante para inventario

- **WHEN** un conector declara inventario solo `entrante` (lee del proveedor, no escribe)
- **THEN** el motor solo aplica cambios del proveedor al canónico
- **AND** no intenta escribir inventario hacia ese proveedor

