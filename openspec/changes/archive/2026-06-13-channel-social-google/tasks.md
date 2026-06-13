## 0. Preparación (OBLIGATORIO)

- [ ] 0.1 Crear y cambiar a la feature branch `feature/channel-social-google` (Step 0 — SIEMPRE primero)
- [ ] 0.2 Leer `openspec/config.yaml`, `docs/integrations-standards.md` y la regla de pasos obligatorios
- [ ] 0.3 Confirmar Sprint 1 implementado; crear apps de desarrollador (Meta, TikTok, Google) y credenciales en el vault

## 1. Adapter de Google Merchant Center (feed)

- [ ] 1.1 `backend/integrations/google_merchant/` con interfaz de adapter y capacidad `catalogo`
- [ ] 1.2 Auth cuenta de servicio/OAuth desde el vault; cliente Content API
- [ ] 1.3 Publicar/actualizar feed de productos (mapeo de IDs); reporte de errores por producto

## 2. Adapter de Meta Commerce

- [ ] 2.1 `backend/integrations/meta/` con interfaz de adapter y capacidades (`catalogo`, `pedidos` si aplica)
- [ ] 2.2 OAuth Graph API en el vault; publicación de catálogo
- [ ] 2.3 Ingesta de pedidos al hub donde haya checkout nativo (idempotente)

## 3. Adapter de TikTok Shop

- [ ] 3.1 `backend/integrations/tiktok/` con interfaz de adapter y capacidades (`catalogo`, `inventario`, `pedidos`)
- [ ] 3.2 OAuth TikTok Shop en el vault; push de catálogo/inventario
- [ ] 3.3 Ingesta de pedidos al hub (webhooks/notificaciones + pull), idempotente

## 4. Revisar y actualizar pruebas (OBLIGATORIO)

- [ ] 4.1 Pruebas de generación/validación de feed (Google) y de catálogo (Meta/TikTok) contra respuestas grabadas/sandbox
- [ ] 4.2 Pruebas de ingesta idempotente de pedidos (Meta/TikTok donde aplique)

## 5. Ejecutar pruebas y verificar estado (OBLIGATORIO — EL AGENTE EJECUTA)

- [ ] 5.1 `ruff check .` sin errores y `pytest` en verde
- [ ] 5.2 Reporte en `specs/channel-social-google/reports/AAAA-MM-DD-step-5-pruebas-y-verificacion.md`

## 6. Verificación manual E2E (OBLIGATORIO — EL AGENTE EJECUTA)

- [ ] 6.1 Publicar catálogo y verificar el feed en cada canal (según acceso/revisión disponible)
- [ ] 6.2 (Meta/TikTok) Crear un pedido de prueba y verificar ingesta al hub + descuento de stock
- [ ] 6.3 Restaurar estado; documentar en el reporte; anotar canales pendientes de revisión de app

## 7. Actualizar documentación (OBLIGATORIO)

- [ ] 7.1 Documentar conectores en `docs/integrations-standards.md` (auth, feed vs pedidos, validación de datos)
- [ ] 7.2 Actualizar `docs/roadmap-plataforma-multicanal.md` (Sprint 4)
- [ ] 7.3 Verificar consistencia documental: 0 referencias rotas
