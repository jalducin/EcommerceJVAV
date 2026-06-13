# stripe-terminal-connector Specification

## Purpose
TBD - created by archiving change pos-payments. Update Purpose after archive.
## Requirements
### Requirement: Adapter de Stripe Terminal para pagos presenciales

El conector de Stripe Terminal SHALL implementar la interfaz de adapter y declarar la capacidad `pagos`
(cobro presencial con lector físico). La autenticación SHALL usar las claves de Stripe en el vault. Es
ejecutable con **test mode** de Stripe.

#### Scenario: Cobro presencial conciliado con el pedido

- **WHEN** se cobra un pedido canónico con un lector de Stripe Terminal
- **THEN** el pago se registra como entidad Pago canónica enlazada al pedido
- **AND** la conciliación es idempotente (un PaymentIntent → un Pago)

#### Scenario: Webhook de pago confirma el cobro

- **WHEN** llega el webhook de Stripe confirmando el PaymentIntent
- **THEN** el Pago canónico pasa a estado pagado y el pedido refleja el cobro
- **AND** un reenvío del webhook no duplica el Pago

