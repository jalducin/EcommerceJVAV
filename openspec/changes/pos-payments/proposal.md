## Why

El POS cierra el canal presencial: ventas en tienda física que también deben consolidarse en el hub de
pedidos y descontar del inventario unificado en tiempo real, además de procesar pagos presenciales. Es el
último sprint porque depende del hub de pedidos e inventario ya consolidados. Sprint 6 del roadmap.

## What Changes

- **Adapters de POS retail**: Square (POS + catálogo + pagos) y Lightspeed — ventas presenciales,
  catálogo e inventario en tienda hacia/desde el hub e inventario unificado.
- **Pagos presenciales**: Stripe Terminal (lector físico), Clip (México) y Conekta (México) — cobro en
  punto de venta y conciliación del pago con el pedido canónico.
- Las ventas POS entran al **hub de pedidos unificado** y descuentan del **inventario unificado** (anti
  sobreventa cruzada con los canales online); los pagos se concilian por pedido.

## Capabilities

### New Capabilities
- `square-connector`: POS, catálogo, inventario y pagos de Square hacia el hub e inventario unificado.
- `lightspeed-connector`: POS retail Lightspeed (ventas, catálogo, inventario).
- `stripe-terminal-connector`: pagos presenciales con Stripe Terminal y conciliación con el pedido.
- `clip-connector`: pagos presenciales Clip (México) y conciliación.
- `conekta-connector`: pagos Conekta (México) y conciliación.

### Modified Capabilities
<!-- Usa unified-orders y unified-inventory (Sprint 1); puede refinar la conciliación de pagos. -->

## Impact

- **Backend**: `backend/integrations/{square,lightspeed,stripe_terminal,clip,conekta}/`; conciliación de
  pago↔pedido en el hub.
- **Datos**: entidad de Pago canónica enlazada al pedido; mapeo de IDs de transacción.
- **Infra**: secretos por proveedor; webhooks de pago/venta; idempotencia de conciliación.
- **Tests**: Square sandbox, Stripe test mode, Conekta/Clip sandbox son gratuitos; Lightspeed requiere
  cuenta.
- **Docs**: sección por conector; flujo de conciliación de pagos.
- **Dependencia**: requiere `integration-platform-core` (Sprint 1) y el hub de pedidos/inventario.
