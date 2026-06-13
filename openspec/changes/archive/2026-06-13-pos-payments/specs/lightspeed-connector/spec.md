## ADDED Requirements

### Requirement: Adapter de Lightspeed sobre el connector framework

El conector de Lightspeed SHALL implementar la interfaz de adapter y declarar las capacidades `catalogo`,
`inventario` y `pedidos` (ventas retail). La autenticación SHALL usar OAuth de Lightspeed en el vault. Es
**deuda técnica diferida** (requiere cuenta retail de pago).

#### Scenario: Venta retail de Lightspeed ingresa al hub

- **WHEN** se registra una venta en Lightspeed
- **THEN** se crea un Pedido canónico con canal de origen `lightspeed`
- **AND** el inventario unificado se descuenta una sola vez (idempotente)
