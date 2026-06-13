# conekta-connector Specification

## Purpose
TBD - created by archiving change pos-payments. Update Purpose after archive.
## Requirements
### Requirement: Adapter de Conekta para pagos (México)

El conector de Conekta SHALL implementar la interfaz de adapter y declarar la capacidad `pagos`. La
autenticación SHALL usar las claves de Conekta en el vault. Es ejecutable con el **sandbox** de Conekta.

#### Scenario: Cobro Conekta conciliado con el pedido

- **WHEN** se cobra un pedido canónico con Conekta
- **THEN** el pago se registra como Pago canónico enlazado al pedido
- **AND** la conciliación es idempotente (un cargo → un Pago)

#### Scenario: Webhook de Conekta confirma el cobro

- **WHEN** llega el webhook de Conekta con firma válida confirmando el cargo
- **THEN** el Pago canónico pasa a estado pagado
- **AND** un reenvío del webhook no duplica el Pago

