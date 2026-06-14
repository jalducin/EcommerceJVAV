## 0. Preparación (OBLIGATORIO)

- [ ] 0.1 Crear y cambiar a la feature branch `feature/store-v2-theme-wishlist-clickcollect` (Step 0 — SIEMPRE primero)
- [ ] 0.2 Leer `openspec/config.yaml`, `docs/backend-standards.md`, `docs/frontend-standards.md` y la regla `.claude/rules/openspec-tasks-mandatory-steps.md`
- [ ] 0.3 Confirmar Sprint 0 (`migrate-to-serverless-aws`: API serverless, `store-configuration`, DynamoDB single-table, JWT de cliente, checkout transaccional) implementado
- [ ] 0.4 Sembrar datos demo (productos con/sin variantes, un usuario cliente, ≥1 ubicación de recogida en la config); levantar el stack local (SAM local + DynamoDB Local)

## 1. store-configuration: tema azul metálico y ubicaciones de recogida

- [ ] 1.1 Redefinir el valor por defecto de `StoreConfig.theme` en `backend/schemas/store.py` a la paleta azul metálico (manteniendo estables los nombres de token)
- [ ] 1.2 Añadir el schema `PickupLocation` (`id`, `name`, `address`, `hours` opcional) y `pickup_locations: list[PickupLocation]` en `StoreConfig` (por defecto lista vacía)
- [ ] 1.3 Verificar que `GET /api/config` expone `pickup_locations` (lista vacía si no hay) y el tema por defecto

## 2. Wishlist: persistencia, repositorio y endpoints

- [ ] 2.1 Añadir `wish_sk(product_id)` y `WISH_SK_PREFIX` en `backend/db/keys.py` (`PK=USER#<id>`, `SK=WISH#<product_id>`)
- [ ] 2.2 Crear `backend/schemas/wishlist.py` (item de entrada y vista de listado)
- [ ] 2.3 Crear `backend/repositories/wishlist_repo.py` con `add` (idempotente), `remove` (idempotente) y `list_items` (query `begins_with(WISH#)`)
- [ ] 2.4 Crear `backend/routers/wishlist.py` con `GET/POST/DELETE /api/wishlist` bajo el JWT de cliente (401 sin sesión; aislamiento por usuario)
- [ ] 2.5 Registrar el router en `backend/main.py`

## 3. Click & collect: checkout con método de entrega

- [ ] 3.1 Añadir `fulfillment` (`ship` | `pickup`, por defecto `ship`) y `pickup_location_id: str | None` a `CheckoutRequest` en `backend/schemas/checkout.py`
- [ ] 3.2 Añadir `fulfillment` y `pickup_location_id` a `Order` en `backend/schemas/checkout.py` (persistencia del método y ubicación)
- [ ] 3.3 En el servicio de checkout: validar `pickup_location_id` contra `store_config.pickup_locations` cuando `fulfillment=pickup` (422 si falta o no existe); rechazar `fulfillment` no reconocido (422)
- [ ] 3.4 En el cálculo de totales: envío 0 si `fulfillment=pickup`; regla de envío vigente si `ship`; descuento de stock transaccional en ambos casos

## 4. Frontend: tema azul, botón de corazón y selector de entrega

- [ ] 4.1 Actualizar los tokens por defecto de `frontend/css/variables.css` a la paleta azul metálico (sin colores hardcodeados, sin frameworks), aplicados vía CSS Custom Properties
- [ ] 4.2 Conectar el botón de corazón del detalle de producto a `POST`/`DELETE /api/wishlist` (alterna estado, estados de carga/error; sin sesión invita a iniciar sesión)
- [ ] 4.3 Añadir en el checkout el selector de método de entrega (envío a domicilio / recoger en tienda) y, en pickup, el selector de ubicación desde `GET /api/config`
- [ ] 4.4 Ocultar/poner en 0 el envío en la vista de checkout cuando `fulfillment=pickup`; responsive 375/768/1280 y estados de carga/vacío/error

## 5. Revisar y actualizar pruebas existentes (OBLIGATORIO)

- [ ] 5.1 Identificar y actualizar las pruebas impactadas del checkout y de `store-configuration` (tema/config)
- [ ] 5.2 Escribir (TDD) las pruebas que fallan para wishlist y para el checkout con `fulfillment` antes de implementar

## 6. Ejecutar pruebas y verificar estado (OBLIGATORIO — EL AGENTE EJECUTA)

- [ ] 6.1 Capturar estado previo (conteos de pedidos/productos y stock de las variantes a usar) antes de las pruebas que mutan estado
- [ ] 6.2 Ejecutar `ruff check .` sin errores y `pytest` dirigido a wishlist + checkout + suite completa en verde
- [ ] 6.3 Verificar y restaurar el estado posterior (revertir pedidos de prueba y restaurar stock e items de wishlist)
- [ ] 6.4 Crear el reporte en `specs/store-v2-theme-wishlist-clickcollect/reports/2026-06-14-step-6-pruebas-y-verificacion.md`

## 7. Verificación manual E2E (OBLIGATORIO — EL AGENTE EJECUTA)

- [ ] 7.1 `GET /api/config`: verificar el tema azul metálico por defecto y `pickup_locations`; verificar que el storefront aplica los tokens (sin colores hardcodeados)
- [ ] 7.2 Wishlist: como cliente, `POST` agregar (verificar idempotencia al repetir), `GET` listar, `DELETE` quitar (verificar idempotencia); `GET` sin token devuelve 401; verificar aislamiento entre dos usuarios
- [ ] 7.3 Botón de corazón en el detalle: alternar con sesión (agrega/quita) y comportamiento sin sesión (invita a iniciar sesión)
- [ ] 7.4 Checkout `ship`: verificar envío según config y creación del pedido; Checkout `pickup` con ubicación válida: envío 0 y pedido con `fulfillment`/`pickup_location_id`
- [ ] 7.5 Casos de error del checkout: `fulfillment` inválido (422), `pickup` sin `pickup_location_id` (422), `pickup` con ubicación inexistente (422); verificar que no se crea pedido
- [ ] 7.6 Verificar responsive 375/768/1280 y estados de carga/vacío/error; restaurar el estado de datos de prueba y documentarlo en el reporte

## 8. Pruebas unitarias de la lógica nueva/cambiada (OBLIGATORIO)

- [ ] 8.1 Pruebas unitarias de `wishlist_repo` en `tests/unit/`: add idempotente, remove idempotente, listado por usuario
- [ ] 8.2 Pruebas unitarias del servicio de checkout en `tests/unit/`: envío 0 en pickup, envío según regla en ship, validación de ubicación (faltante/inexistente → 422), `fulfillment` inválido

## 9. Actualizar documentación técnica (OBLIGATORIO)

- [ ] 9.1 Documentar las claves DynamoDB de wishlist (`PK=USER#<id>`, `SK=WISH#<product_id>`) y el `fulfillment` del checkout en `docs/backend-standards.md`
- [ ] 9.2 Documentar el tema azul metálico por defecto y el patrón del botón de corazón en `docs/frontend-standards.md`
- [ ] 9.3 Verificar consistencia documental: una fuente canónica por dato y 0 referencias rotas

## 10. Actualizar el runbook del cliente (OBLIGATORIO)

- [ ] 10.1 Actualizar/crear el runbook del cliente en `docs/runbooks/` (Objetivo, Precondiciones, Pasos, Verificación, Troubleshooting) con el uso de la lista de deseos y la opción de recoger en tienda en el checkout

## 11. Documentación Swagger/OpenAPI al día (OBLIGATORIO)

- [ ] 11.1 Documentar el contrato OpenAPI de `GET/POST/DELETE /api/wishlist` (summary, description, tags, response_model, errores 401)
- [ ] 11.2 Actualizar el contrato OpenAPI del checkout con `fulfillment`/`pickup_location_id` (errores 422) y de `GET /api/config` con `pickup_locations`, de modo que `/docs` y `/openapi.json` reflejen el contrato real
