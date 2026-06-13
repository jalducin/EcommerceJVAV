## 0. Preparación (OBLIGATORIO)

- [ ] 0.1 Crear y cambiar a la feature branch `feature/panel-admin` (Step 0 — SIEMPRE primero)
- [ ] 0.2 Leer `openspec/config.yaml`, `docs/frontend-standards.md`, `docs/backend-standards.md` y la regla `.claude/rules/openspec-tasks-mandatory-steps.md`
- [ ] 0.3 Confirmar Sprint 0 (`migrate-to-serverless-aws`: API serverless, store-config, rol admin/`require_admin`) y Sprint 1 (`integration-platform-core`: registro de conectores, hub de pedidos, observabilidad) implementados
- [ ] 0.4 Sembrar datos demo y un usuario admin; levantar el stack local (SAM local + DynamoDB Local)

## 1. Endpoints admin de backend (dashboard, pedidos, estado)

- [ ] 1.1 Crear `backend/routers/admin.py` con prefijo `/api/admin`, todos los endpoints con `Depends(require_admin)`
- [ ] 1.2 `GET /api/admin/dashboard`: servicio de agregación (ventas del día storefront + hub de canales, pedidos pendientes, stock bajo, salud de conectores)
- [ ] 1.3 `GET /api/admin/orders`: listado unificado (storefront + `integrations/channel_orders`) con filtro por estado y por canal; normalizar shape con `channel` de origen
- [ ] 1.4 Endpoint de cambio de estado de pedido con validación de transición (404 inexistente, 422 transición inválida)
- [ ] 1.5 Schemas Pydantic de entrada/salida para dashboard, listado y cambio de estado

## 2. Backend de conectores (vista admin)

- [ ] 2.1 Endpoint admin de estado de conectores: por conector último sync, en cola, DLQ y flag `deferred` (registro + observabilidad del Sprint 1)
- [ ] 2.2 Endpoint admin para habilitar/deshabilitar un conector (registrar/quitar del registro)

## 3. Frontend: auth, guard y tema

- [ ] 3.1 `frontend/admin/login.html` + `frontend/js/admin/auth.js`: login contra `/api/auth/login`, JWT en localStorage, refresh automático
- [ ] 3.2 Guard de vistas admin (redirige a login sin sesión; muestra 403 si no es admin)
- [ ] 3.3 Cargar tema desde `GET /api/config` y aplicarlo vía CSS Custom Properties (sin colores hardcodeados, sin frameworks)

## 4. Frontend: vistas del panel

- [ ] 4.1 Vista de productos: CRUD sobre `/api/products` con editor de variantes (atributos arbitrarios), selector de categoría desde config, soft delete
- [ ] 4.2 Vista de dashboard: tarjetas de ventas del día, pedidos pendientes, stock bajo y salud de conectores
- [ ] 4.3 Vista de pedidos: listado unificado con filtros y cambio de estado
- [ ] 4.4 Vista de conectores: estado de sync, marca `deferred`, habilitar/deshabilitar
- [ ] 4.5 Estados de carga/vacío/error en todas las vistas y accesibilidad (labels, aria, contraste); responsive 375/768/1280

## 5. Revisar y actualizar pruebas (OBLIGATORIO)

- [ ] 5.1 Pruebas de los endpoints admin: 200 con admin, 401 sin token, 403 sin rol admin
- [ ] 5.2 Pruebas de agregación del dashboard (ventas storefront + canal sin doble conteo; pendientes; stock bajo)
- [ ] 5.3 Pruebas del listado unificado de pedidos (filtro por canal/estado) y del cambio de estado (válido, 422, 404)
- [ ] 5.4 Pruebas del endpoint de conectores (estado y habilitar/deshabilitar)

## 6. Ejecutar pruebas y verificar estado (OBLIGATORIO — EL AGENTE EJECUTA)

- [ ] 6.1 Capturar estado previo (conteos de pedidos/productos) antes de las pruebas que mutan estado
- [ ] 6.2 Ejecutar `ruff check .` sin errores y `pytest` dirigido al módulo admin + suite completa en verde
- [ ] 6.3 Verificar y restaurar el estado posterior (revertir pedidos/productos de prueba)
- [ ] 6.4 Crear el reporte en `specs/panel-admin/reports/AAAA-MM-DD-step-6-pruebas-y-verificacion.md`

## 7. Verificación manual E2E del panel (OBLIGATORIO — EL AGENTE EJECUTA)

- [ ] 7.1 Login como admin y verificar acceso al dashboard; login como no-admin y verificar 403/redirect en vistas admin
- [ ] 7.2 Crear, editar y desactivar un producto con variantes desde la UI; verificar validación de categoría (422)
- [ ] 7.3 Verificar el dashboard: ventas del día (con un pedido de storefront y uno de canal), pendientes, stock bajo, salud de conectores
- [ ] 7.4 Listar pedidos unificados, filtrar por canal y cambiar el estado de un pedido (verificar 404/422 en casos inválidos)
- [ ] 7.5 Ver estado de conectores, habilitar/deshabilitar uno y verificar el reflejo; verificar estado vacío sin conectores
- [ ] 7.6 Verificar responsive en 375/768/1280 y estados de carga/vacío/error; restaurar el estado de datos de prueba y documentarlo en el reporte

## 8. Actualizar documentación (OBLIGATORIO)

- [ ] 8.1 Documentar el panel y sus patrones (auth, guard, accesibilidad, tema) en `docs/frontend-standards.md`
- [ ] 8.2 Documentar el contrato de los endpoints admin (`/api/admin/dashboard`, `/api/admin/orders`, cambio de estado, conectores)
- [ ] 8.3 Actualizar `docs/roadmap-plataforma-multicanal.md` (marcar Sprint 7 en progreso/listo)
- [ ] 8.4 Verificar consistencia documental: una fuente canónica por dato y 0 referencias rotas
