## Context

Sprint 6: canal presencial (POS) y pagos. Las ventas en tienda deben consolidarse en el **hub de pedidos**
y descontar del **inventario unificado** en tiempo real (anti-sobreventa cruzada con online), y los pagos
presenciales deben conciliarse con el pedido canónico. Depende del hub e inventario del Sprint 1. Es el
último sprint por esa dependencia.

## Goals / Non-Goals

**Goals:**
- POS (Square, Lightspeed): ventas/catálogo/inventario en tienda ↔ hub e inventario unificado.
- Pagos presenciales (Stripe Terminal, Clip, Conekta): cobro y **conciliación pago↔pedido** idempotente.
- Entidad Pago canónica enlazada al pedido, con estados y mapeo de id de transacción.

**Non-Goals:**
- Hardware/aprovisionamiento de lectores (fuera del software); se asume el lector configurado.
- Reportería financiera/contable avanzada; alcance: conciliación de pago con pedido.

## Decisions

### Decisión 1: POS = canal de pedidos sobre el hub
Square/Lightspeed se modelan como canales que generan Pedidos canónicos y descuentan inventario unificado,
reutilizando `unified-orders` y `unified-inventory` del Sprint 1 (anti-sobreventa con online).

### Decisión 2: Pago como entidad canónica enlazada al pedido
Se materializa la entidad Pago (del modelo canónico del Sprint 1): un pedido puede tener uno o más Pagos;
cada Pago mapea a la transacción del proveedor. La conciliación es idempotente por id de transacción.

### Decisión 3: Confirmación por webhook + idempotencia
Stripe (PaymentIntent + webhook), Clip y Conekta (webhook con firma) confirman el cobro asíncronamente. El
reenvío de webhooks no duplica el Pago (idempotencia por id de transacción / clave de evento del Sprint 1).

### Decisión 4: Sandbox-first; Lightspeed diferido
Square sandbox, Stripe test mode, Clip y Conekta sandbox son gratuitos → ejecutables. Lightspeed requiere
cuenta retail de pago → deuda técnica diferida (política tier 0).

## Risks / Trade-offs

- **Sobreventa tienda vs online** → descuento siempre contra inventario unificado (condicional); POS en tiempo real.
- **Doble cobro / doble registro** → idempotencia por id de transacción y por clave de evento de webhook.
- **Desconexión del lector / pagos offline** → fuera de alcance base; documentar como limitación.
- **Acceso a Lightspeed** → diferir como deuda técnica; no bloquea los demás.

## Migration Plan

1. Materializar entidad Pago canónica y su enlace al pedido (conciliación).
2. Pagos ejecutables: Stripe Terminal (test), Clip y Conekta (sandbox) con webhooks idempotentes.
3. POS: Square (sandbox) ventas/catálogo/inventario ↔ hub e inventario unificado.
4. Diferido: Lightspeed (codificado; verificación al tener cuenta).

## Open Questions

- ¿Pagos parciales/propinas/reembolsos en el alcance, o solo cobro completo + reembolso básico?
- ¿Conciliación de cierre de caja (settlement) por proveedor en este sprint o como evolución?
