# unified-orders Specification

## Purpose
TBD - created by archiving change integration-platform-core. Update Purpose after archive.
## Requirements
### Requirement: Hub de pedidos unificado

El sistema SHALL consolidar los pedidos de todos los canales (online, marketplaces, social, POS) en el
modelo de Pedido canónico, conservando el **canal de origen** y el id externo. Un pedido de cualquier
canal SHALL ser consultable de forma uniforme desde el hub.

#### Scenario: Pedidos de varios canales en el hub

- **WHEN** entran pedidos desde Shopify, MercadoLibre y POS
- **THEN** los tres quedan como Pedidos canónicos en el hub con su canal de origen
- **AND** se listan y consultan con la misma estructura

### Requirement: Ingesta idempotente y deduplicada de pedidos

La ingesta de un pedido externo SHALL ser idempotente y deduplicada usando el mapeo de IDs: reingresar el
mismo pedido externo NO SHALL crear un duplicado canónico.

#### Scenario: Reingesta del mismo pedido externo

- **WHEN** el mismo pedido de un canal se ingesta dos veces (webhook + reconciliación por pull)
- **THEN** existe un único Pedido canónico para ese id externo
- **AND** la segunda ingesta actualiza, no duplica

### Requirement: Sincronización de estado de fulfillment

Los cambios de estado del pedido (p. ej. enviado, entregado, cancelado) SHALL sincronizarse entre el
canónico y el canal de origen según las capacidades del conector.

#### Scenario: Cambio de estado se refleja en el canal de origen

- **WHEN** un pedido canónico pasa a `enviado`
- **THEN** el motor encola la actualización de fulfillment hacia el canal de origen
- **AND** el canal refleja el nuevo estado si su conector soporta fulfillment

