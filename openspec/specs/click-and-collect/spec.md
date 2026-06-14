# click-and-collect Specification

## Purpose
TBD - created by archiving change store-v2-theme-wishlist-clickcollect. Update Purpose after archive.
## Requirements
### Requirement: Selección de método de entrega en el checkout

El checkout SHALL aceptar un método de entrega (`fulfillment`) con los valores `ship` (envío a domicilio) o
`pickup` (recoger en tienda). El valor por defecto SHALL ser `ship` para mantener la retrocompatibilidad de
los clientes e integraciones que no envíen el campo. Cuando `fulfillment` sea `pickup`, la solicitud SHALL
incluir un `pickup_location_id` que identifique una ubicación de recogida declarada en la configuración de
tienda. Un valor de `fulfillment` no reconocido SHALL responder 422.

#### Scenario: Checkout con envío a domicilio por defecto

- **WHEN** un cliente completa el checkout sin especificar `fulfillment`
- **THEN** el pedido se procesa como `ship` (envío a domicilio)
- **AND** se aplica la regla de envío vigente de la configuración de tienda

#### Scenario: Checkout con recoger en tienda

- **WHEN** un cliente completa el checkout con `fulfillment=pickup` y un `pickup_location_id` válido
- **THEN** el pedido se procesa como recogida en esa ubicación
- **AND** se descuenta el stock de las variantes de forma transaccional, igual que en el envío a domicilio

#### Scenario: Método de entrega inválido

- **WHEN** el checkout recibe un `fulfillment` que no es `ship` ni `pickup`
- **THEN** el backend responde 422
- **AND** no se crea el pedido

### Requirement: Validación de la ubicación de recogida

Cuando `fulfillment` sea `pickup`, el backend SHALL validar que el `pickup_location_id` corresponda a una
ubicación declarada en `store_config.pickup_locations`. Si falta el `pickup_location_id` o no corresponde a
ninguna ubicación configurada, el backend SHALL responder 422 y NO SHALL crear el pedido. La validación de
la ubicación SHALL ser autoridad del backend; el cliente NO SHALL poder forzar una ubicación inexistente.

#### Scenario: Ubicación de recogida válida

- **WHEN** el checkout es `pickup` con un `pickup_location_id` presente en la configuración
- **THEN** el pedido se crea asociado a esa ubicación de recogida

#### Scenario: Ubicación de recogida inexistente

- **WHEN** el checkout es `pickup` con un `pickup_location_id` que no existe en la configuración
- **THEN** el backend responde 422 indicando ubicación de recogida inválida
- **AND** no se crea el pedido

#### Scenario: Recogida sin ubicación

- **WHEN** el checkout es `pickup` pero no incluye `pickup_location_id`
- **THEN** el backend responde 422
- **AND** no se crea el pedido

### Requirement: Envío no cobrado en recogida en tienda y persistido en el pedido

Cuando `fulfillment` sea `pickup`, el cálculo de totales SHALL fijar el envío en 0 (no se cobra envío),
independientemente de la regla de envío de la configuración. Cuando sea `ship`, SHALL aplicarse la regla de
envío vigente. El pedido creado SHALL persistir el método de entrega (`fulfillment`) y, cuando aplique, el
`pickup_location_id`, de modo que el método y la ubicación queden trazables en el pedido.

#### Scenario: Envío en cero al recoger en tienda

- **WHEN** se calculan los totales de un checkout con `fulfillment=pickup`
- **THEN** el envío del pedido es 0, sin importar el `shipping_flat` configurado
- **AND** el subtotal e impuesto se calculan con las reglas vigentes

#### Scenario: Envío aplicado al enviar a domicilio

- **WHEN** se calculan los totales de un checkout con `fulfillment=ship`
- **THEN** el envío se calcula con la regla de envío de la configuración de tienda

#### Scenario: El pedido guarda método y ubicación de entrega

- **WHEN** se crea un pedido con `fulfillment=pickup` y una ubicación válida
- **THEN** el pedido persiste `fulfillment=pickup` y el `pickup_location_id` usado
- **AND** un pedido con `fulfillment=ship` persiste el método de envío sin `pickup_location_id`

