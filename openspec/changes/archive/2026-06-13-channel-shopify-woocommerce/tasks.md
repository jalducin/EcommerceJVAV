## 0. Preparación (OBLIGATORIO)

- [ ] 0.1 Crear y cambiar a la feature branch `feature/channel-shopify-woocommerce` (Step 0 — SIEMPRE primero)
- [ ] 0.2 Leer `openspec/config.yaml`, `docs/integrations-standards.md` y la regla de pasos obligatorios
- [ ] 0.3 Confirmar que el Sprint 1 (`integration-platform-core`) está implementado (framework, sync-engine, hub, vault)
- [ ] 0.4 Preparar entornos de prueba: Shopify development store y WooCommerce local (con claves en el vault)

## 1. Adapter de Shopify

- [ ] 1.1 Implementar `backend/integrations/shopify/` con la interfaz de adapter y capacidades declaradas
- [ ] 1.2 Auth con token/OAuth desde el vault; cliente HTTP con rate limiting de Shopify
- [ ] 1.3 Push de catálogo/inventario (mapeo de IDs, crear si no existe)
- [ ] 1.4 Webhook `orders/create` con verificación HMAC + ingesta al hub (idempotente)
- [ ] 1.5 Reconciliación por pull de pedidos (respaldo) y sync de fulfillment

## 2. Adapter de WooCommerce

- [ ] 2.1 Implementar `backend/integrations/woocommerce/` con la interfaz de adapter y capacidades
- [ ] 2.2 Auth con consumer key/secret desde el vault; cliente HTTP con rate limiting
- [ ] 2.3 Push de catálogo/inventario (mapeo de IDs)
- [ ] 2.4 Webhook de pedidos con verificación de firma + ingesta al hub (idempotente)
- [ ] 2.5 Reconciliación por pull y sync de fulfillment

## 3. Revisar y actualizar pruebas (OBLIGATORIO)

- [ ] 3.1 Pruebas de cada adapter contra respuestas grabadas/mock y, si hay acceso, dev store / Woo local
- [ ] 3.2 Pruebas de ingesta idempotente de pedidos (webhook duplicado, pull tras webhook)
- [ ] 3.3 Prueba de anti-sobreventa con Shopify y WooCommerce activos simultáneamente

## 4. Ejecutar pruebas y verificar estado (OBLIGATORIO — EL AGENTE EJECUTA)

- [ ] 4.1 `ruff check .` sin errores y `pytest` en verde
- [ ] 4.2 Reporte en `specs/channel-shopify-woocommerce/reports/AAAA-MM-DD-step-4-pruebas-y-verificacion.md`

## 5. Verificación manual E2E (OBLIGATORIO — EL AGENTE EJECUTA)

- [ ] 5.1 Publicar un producto canónico y verificar que aparece en Shopify y WooCommerce
- [ ] 5.2 Crear un pedido en cada plataforma y verificar que entra al hub unificado y descuenta inventario
- [ ] 5.3 Vender la última unidad en un canal y verificar que el otro no sobrevende
- [ ] 5.4 Restaurar estado (despublicar/cancelar pedidos de prueba); documentar en el reporte

## 6. Actualizar documentación (OBLIGATORIO)

- [ ] 6.1 Documentar ambos conectores en `docs/integrations-standards.md` (auth, webhooks, rate limits)
- [ ] 6.2 Actualizar `docs/roadmap-plataforma-multicanal.md` (marcar Sprint 2 en progreso/listo)
- [ ] 6.3 Verificar consistencia documental: 0 referencias rotas
