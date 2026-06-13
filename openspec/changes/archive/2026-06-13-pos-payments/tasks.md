## 0. Preparación (OBLIGATORIO)

- [ ] 0.1 Crear y cambiar a la feature branch `feature/pos-payments` (Step 0 — SIEMPRE primero)
- [ ] 0.2 Leer `openspec/config.yaml`, `docs/integrations-standards.md` y la regla de pasos obligatorios
- [ ] 0.3 Confirmar Sprint 1 implementado (hub de pedidos + inventario unificado + entidad Pago canónica)
- [ ] 0.4 Crear sandboxes: Square, Stripe (test), Clip, Conekta; credenciales en el vault

## 1. Entidad Pago y conciliación (base del sprint)

- [ ] 1.1 Materializar la entidad Pago canónica enlazada al pedido (estados, id de transacción, mapeo de IDs)
- [ ] 1.2 Lógica de conciliación pago↔pedido idempotente por id de transacción

## 2. Pagos ejecutables (Stripe Terminal, Clip, Conekta)

- [ ] 2.1 `backend/integrations/stripe_terminal/` — PaymentIntent + webhook idempotente (test mode)
- [ ] 2.2 `backend/integrations/clip/` — cobro + webhook con firma (sandbox)
- [ ] 2.3 `backend/integrations/conekta/` — cobro + webhook con firma (sandbox)

## 3. POS (Square ejecutable, Lightspeed diferido)

- [ ] 3.1 `backend/integrations/square/` — ventas→hub, catálogo/inventario↔unificado, pagos (sandbox)
- [ ] 3.2 `backend/integrations/lightspeed/` — estructura + OAuth (DEUDA TÉCNICA: verificación diferida por cuenta de pago)

## 4. Revisar y actualizar pruebas (OBLIGATORIO)

- [ ] 4.1 Pruebas de conciliación de pago idempotente (webhook duplicado no duplica Pago)
- [ ] 4.2 Pruebas de venta POS → pedido en el hub + descuento de inventario unificado
- [ ] 4.3 Prueba anti-sobreventa tienda vs online (POS + un canal online activos)

## 5. Ejecutar pruebas y verificar estado (OBLIGATORIO — EL AGENTE EJECUTA)

- [ ] 5.1 `ruff check .` sin errores y `pytest` en verde
- [ ] 5.2 Reporte en `specs/pos-payments/reports/AAAA-MM-DD-step-5-pruebas-y-verificacion.md`

## 6. Verificación manual E2E (OBLIGATORIO — EL AGENTE EJECUTA)

- [ ] 6.1 Cobro presencial (Stripe test / Clip / Conekta sandbox) y verificar Pago conciliado con el pedido
- [ ] 6.2 Venta en Square (sandbox) y verificar pedido en el hub + descuento de inventario
- [ ] 6.3 Reenviar un webhook de pago y verificar que no duplica el Pago
- [ ] 6.4 Restaurar estado (reembolsar/cancelar pruebas); documentar en el reporte; anotar Lightspeed diferido

## 7. Actualizar documentación (OBLIGATORIO)

- [ ] 7.1 Documentar conectores y el flujo de conciliación de pagos en `docs/integrations-standards.md`
- [ ] 7.2 Actualizar `docs/roadmap-plataforma-multicanal.md` (Sprint 6; Lightspeed como deuda técnica)
- [ ] 7.3 Verificar consistencia documental: 0 referencias rotas
