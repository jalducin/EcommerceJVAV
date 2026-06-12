## ADDED Requirements

### Requirement: Adapter de Clip para pagos presenciales (México)

El conector de Clip SHALL implementar la interfaz de adapter y declarar la capacidad `pagos` (cobro
presencial en México). La autenticación SHALL usar las credenciales de Clip en el vault. Es ejecutable con
el **sandbox** de Clip.

#### Scenario: Cobro Clip conciliado con el pedido

- **WHEN** se cobra un pedido canónico con Clip
- **THEN** el pago se registra como Pago canónico enlazado al pedido
- **AND** la conciliación es idempotente (una transacción → un Pago)

#### Scenario: Webhook de Clip confirma el cobro

- **WHEN** llega el webhook de Clip con firma válida confirmando la transacción
- **THEN** el Pago canónico pasa a estado pagado
- **AND** un reenvío del webhook no duplica el Pago
