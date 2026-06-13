## 0. Preparación (OBLIGATORIO)

- [ ] 0.1 Crear y cambiar a la feature branch `feature/sprint-8-runbooks-tests-swagger` (Step 0 — SIEMPRE primero)
- [ ] 0.2 Leer `openspec/config.yaml`, `docs/base-standards.md`, `docs/backend-standards.md`, `docs/integrations-standards.md`, `docs/documentation-standards.md` y la regla `.claude/rules/openspec-tasks-mandatory-steps.md`
- [ ] 0.3 Confirmar Sprints 0–7 implementados (API serverless con routers auth/config/catalog/cart/orders, núcleo de integración, conectores y panel admin)
- [ ] 0.4 Sembrar datos demo y levantar el stack local (SAM local + DynamoDB Local) para poder ejecutar los runbooks y la verificación

## 1. Capability `user-runbooks` — runbooks por tipo de usuario

- [ ] 1.1 Crear `docs/runbooks/README.md` (índice que enlaza los cuatro runbooks por tipo de usuario)
- [ ] 1.2 `docs/runbooks/visitante.md`: navegar/buscar catálogo (objetivo, precondiciones, pasos sobre `GET /api/products`, verificación, troubleshooting)
- [ ] 1.3 `docs/runbooks/cliente.md`: registro/login, carrito, checkout y ver pedidos (`/api/auth`, `/api/cart`, `/api/orders`), con verificación y troubleshooting
- [ ] 1.4 `docs/runbooks/administrador.md`: catálogo con variantes, pedidos, dashboard y conectores (panel admin + `/api/products` y `/api/admin/*`), con precondición de rol admin
- [ ] 1.5 `docs/runbooks/operador-devops.md`: deploy SAM, seed, rotación de secretos del vault, teardown y lectura de logs/DLQ, con verificación y troubleshooting
- [ ] 1.6 Asegurar que cada runbook tiene las cinco secciones obligatorias (Objetivo, Precondiciones, Pasos, Verificación, Troubleshooting) en orden

## 2. Capability `api-swagger` — documentación OpenAPI/Swagger

- [ ] 2.1 Configurar `backend/app.py`: metadatos de `FastAPI(...)` (título, versión, descripción), `openapi_tags` con descripción por tag y exposición de `/docs` y `/openapi.json`
- [ ] 2.2 Enriquecer `routers/accounts.py` (auth): `summary`/`description`/`response_model`/`responses` (401/422) por operación
- [ ] 2.3 Enriquecer `routers/store.py` (config) y `routers/catalog.py` (products): summaries, descriptions, response models y respuestas de error (404/422)
- [ ] 2.4 Enriquecer `routers/cart_dynamo.py` (cart) y `routers/orders_dynamo.py` (orders): summaries, descriptions, response models y errores (401/404/422)
- [ ] 2.5 Enriquecer el router admin (`/api/admin/*`, Sprint 7): summaries, descriptions, response models y 401/403; declarar el esquema de seguridad bearer JWT
- [ ] 2.6 Documentar en `docs/integrations-standards.md` el contrato de cada conector no-HTTP de `backend/integrations/connectors/` (capacidades, dirección de sync, payload canónico, mapeo de IDs), marcando los diferidos
- [ ] 2.7 Verificar que `/docs` y `/openapi.json` no exponen secretos y que en producción quedan deshabilitados/protegidos salvo flag

## 3. Capability `unit-test-suite` — suite de pruebas unitarias

- [ ] 3.1 Documentar la convención en `docs/backend-standards.md`: `tests/unit/` vs `tests/integration/`, naming, aislamiento con moto/mocks y objetivo de cobertura ≥85%
- [ ] 3.2 Configurar `pytest --cov=backend` (pyproject/pytest.ini) con umbral de cobertura y exclusiones (arranque/handlers triviales)
- [ ] 3.3 Pruebas unitarias de repositorios (`backend/repositories/`) con DynamoDB mockeado (moto): éxito y error
- [ ] 3.4 Pruebas unitarias de servicios (`backend/cart_service.py`, `backend/services/`): caminos de éxito y error
- [ ] 3.5 Pruebas unitarias del framework de integración (`connector.py`, `canonical.py`, `mapping.py`) y de cada conector (traducción a canónico, capacidades, dirección de sync) con clientes externos mockeados
- [ ] 3.6 Pruebas unitarias de `backend/pricing.py` (totales, casos límite) y `backend/security.py` (hash/verify de contraseña, emisión/decodificación de tokens, token inválido/expirado)

## 4. Revisar y actualizar pruebas (OBLIGATORIO)

- [ ] 4.1 Identificar y actualizar pruebas existentes impactadas por el enriquecimiento OpenAPI y por la reorganización `tests/unit/` vs `tests/integration/`
- [ ] 4.2 Verificar que ninguna prueba de integración quedó contabilizada como unitaria para el objetivo de cobertura

## 5. Ejecutar pruebas y verificar estado (OBLIGATORIO — EL AGENTE EJECUTA)

- [ ] 5.1 Capturar estado previo (conteos de datos demo) antes de pruebas que muten estado
- [ ] 5.2 Ejecutar `ruff check .` sin errores y `pytest --cov=backend` con la suite completa en verde y cobertura ≥85%
- [ ] 5.3 Verificar y restaurar el estado posterior si alguna prueba mutó datos
- [ ] 5.4 Crear el reporte en `specs/sprint-8-runbooks-tests-swagger/reports/AAAA-MM-DD-step-5-pruebas-y-verificacion.md` (comandos, resultados, cobertura, estado)

## 6. Verificación manual (OBLIGATORIO — EL AGENTE EJECUTA)

- [ ] 6.1 Ejecutar el runbook del visitante de punta a punta y verificar el resultado (catálogo listado/buscado sin sesión)
- [ ] 6.2 Ejecutar el runbook del cliente (registro/login, carrito, checkout, ver pedidos) y verificar la creación del pedido
- [ ] 6.3 Ejecutar el runbook del administrador (catálogo con variantes, pedidos, dashboard, conectores) verificando el acceso 403 sin rol admin
- [ ] 6.4 Ejecutar el runbook del operador/DevOps en local (deploy SAM/seed, `GET /api/health`, lectura de logs/DLQ, rotación de secreto en sandbox) y restaurar el estado
- [ ] 6.5 Abrir `GET /docs` y `GET /openapi.json`: verificar que todos los routers aparecen con tags, summaries, response models y errores; validar el esquema OpenAPI

## 7. Actualizar documentación técnica (OBLIGATORIO)

- [ ] 7.1 Actualizar `docs/base-standards.md` con la nueva §9 "Entregables transversales obligatorios" (runbook + pruebas unitarias + Swagger)
- [ ] 7.2 Confirmar que `docs/backend-standards.md` (convención de pruebas) y `docs/integrations-standards.md` (contratos de conectores) quedan al día
- [ ] 7.3 Actualizar el índice/inventario de documentación si aplica y `docs/roadmap-plataforma-multicanal.md` (marcar Sprint 8)
- [ ] 7.4 Verificar consistencia documental: una fuente canónica por dato y 0 referencias rotas

## 8. Entregables transversales del cambio (OBLIGATORIO — regla SDD §9)

- [ ] 8.1 Actualizar/crear el runbook de cada tipo de usuario afectado por este cambio (los cuatro runbooks de la capability `user-runbooks`)
- [ ] 8.2 Incluir pruebas unitarias de toda la lógica nueva/cambiada (la suite de la capability `unit-test-suite`)
- [ ] 8.3 Mantener al día la documentación Swagger/OpenAPI de los endpoints afectados (`/docs`, `/openapi.json` y los routers enriquecidos)
