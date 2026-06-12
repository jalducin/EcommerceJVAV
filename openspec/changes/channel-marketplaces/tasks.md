## 0. Preparación (OBLIGATORIO)

- [ ] 0.1 Crear y cambiar a la feature branch `feature/channel-marketplaces` (Step 0 — SIEMPRE primero)
- [ ] 0.2 Leer `openspec/config.yaml`, `docs/integrations-standards.md` y la regla de pasos obligatorios
- [ ] 0.3 Confirmar Sprint 1 implementado; preparar test users de MercadoLibre (gratis)

## 1. Adapter de MercadoLibre (ejecutable)

- [ ] 1.1 `backend/integrations/mercadolibre/` con interfaz de adapter y capacidades (catálogo/inventario/pedidos)
- [ ] 1.2 OAuth 2.0 + refresh en el vault; cliente HTTP con rate limiting
- [ ] 1.3 Publicaciones e inventario push (mapeo de IDs)
- [ ] 1.4 Notificaciones (topics) + pull de Orders API → ingesta idempotente al hub
- [ ] 1.5 Sync de fulfillment básico

## 2. Adapter de Amazon SP-API (DEUDA TÉCNICA — implementación diferida)

- [ ] 2.1 `backend/integrations/amazon/` con interfaz de adapter y capacidades (estructura lista)
- [ ] 2.2 Auth LWA + refresh en el vault (codificado; verificación diferida por falta de cuenta)
- [ ] 2.3 Feeds de listings/inventario y Orders API + notificaciones (codificado)
- [ ] 2.4 DIFERIDO: dejar sin marcar como completo hasta tener cuenta de vendedor + aprobación; registrar en el roadmap

## 3. Revisar y actualizar pruebas (OBLIGATORIO)

- [ ] 3.1 Pruebas de MercadoLibre contra test users y/o respuestas grabadas
- [ ] 3.2 Pruebas de Amazon contra respuestas grabadas/mock (sin cuenta real)
- [ ] 3.3 Ingesta idempotente y anti-sobreventa con un marketplace activo + un canal del Sprint 2

## 4. Ejecutar pruebas y verificar estado (OBLIGATORIO — EL AGENTE EJECUTA)

- [ ] 4.1 `ruff check .` sin errores y `pytest` en verde
- [ ] 4.2 Reporte en `specs/channel-marketplaces/reports/AAAA-MM-DD-step-4-pruebas-y-verificacion.md`

## 5. Verificación manual E2E (OBLIGATORIO — EL AGENTE EJECUTA)

- [ ] 5.1 (MercadoLibre) Publicar un item, crear un pedido con test user y verificar ingesta al hub + descuento de stock
- [ ] 5.2 Verificar reconciliación por pull no duplica
- [ ] 5.3 Restaurar estado (cerrar publicaciones/pedidos de prueba); documentar en el reporte
- [ ] 5.4 (Amazon) DIFERIDO: verificación pendiente de acceso

## 6. Actualizar documentación (OBLIGATORIO)

- [ ] 6.1 Documentar conectores en `docs/integrations-standards.md` (auth, notificaciones, rate limits)
- [ ] 6.2 Actualizar `docs/roadmap-plataforma-multicanal.md` (Sprint 3; Amazon como deuda técnica diferida)
- [ ] 6.3 Verificar consistencia documental: 0 referencias rotas
