## 0. Preparación (OBLIGATORIO)

- [ ] 0.1 Crear y cambiar a la feature branch `feature/migrate-to-serverless-aws` (Step 0 — SIEMPRE primero)
- [ ] 0.2 Leer `openspec/config.yaml`, `docs/backend-standards.md` y `.claude/rules/openspec-tasks-mandatory-steps.md`
- [ ] 0.3 Instalar prerequisitos locales: AWS SAM CLI, DynamoDB Local (Docker), AWS CLI; configurar perfil/región
- [ ] 0.4 Definir presupuesto/alarma de billing en AWS para proteger el free tier (tier 0)

## 1. Infraestructura base (SAM + DynamoDB)

- [ ] 1.1 Crear `template.yaml` (SAM) con Lambda (Mangum), HTTP API, tabla DynamoDB + GSIs (GSI1 email, GSI2 categoría, GSI3 pedidos)
- [ ] 1.2 Definir roles IAM de mínimo privilegio (DynamoDB tabla+GSIs, SES)
- [ ] 1.3 Configurar DynamoDB Local (Docker) y script para crear la tabla+GSIs en local
- [ ] 1.4 Añadir dependencias: +`mangum`, +`boto3`/`aioboto3`; planificar retiro de `alembic`, `slowapi`, `aiosqlite`

## 2. Capa de datos DynamoDB (reemplaza SQLAlchemy)

- [ ] 2.1 Crear cliente/repositorio DynamoDB y utilidades de claves (PK/SK, GSIs) detrás de `services/`
- [ ] 2.2 Migrar `User` (PROFILE + GSI email) y ajustar `services/auth.py` (login por email, current_user)
- [ ] 2.3 Migrar `Product` con **variantes y atributos arbitrarios** (`backend/schemas/product.py`) y `services/products.py` (listar por categoría, filtros, paginación, detalle, CRUD admin)
- [ ] 2.4 Migrar `CartItem` (`USER#<id>` / `CART#...`) y `services/cart.py` (CRUD + sync localStorage→DynamoDB)
- [ ] 2.5 Migrar `Order`/checkout con `TransactWriteItems` (crear pedido + descuento de stock condicional) en `services/order.py`
- [ ] 2.6 Migrar métricas admin (`services/admin.py`): ventas del día, pedidos pendientes, stock bajo (Scan acotado/GSI)
- [ ] 2.7 Eliminar `backend/database.py` (SQLAlchemy), `backend/models/*`, `alembic/`, `alembic.ini`

## 3. Configuración de tienda (business-agnostic)

- [ ] 3.1 Modelar `StoreConfig` (`CONFIG/STORE`) y schema Pydantic (marca, categorías, moneda, locale, impuesto/envío, tema)
- [ ] 3.2 Endpoint `GET /api/config` que expone la configuración vigente
- [ ] 3.3 Hacer el cálculo de totales (carrito/checkout) data-driven según impuesto/envío/moneda de la config
- [ ] 3.4 Validar categoría de producto contra la config (rechazar inválidas con 422)

## 4. Adaptación del runtime serverless

- [ ] 4.1 `backend/main.py`: añadir `handler = Mangum(app)`, quitar mount de `StaticFiles`, CORS para dominio CloudFront
- [ ] 4.2 Reemplazar `slowapi`/`limiter.py` por throttling de login en API Gateway (definido en SAM)
- [ ] 4.3 `backend/utils/email.py`: enviar confirmación por SES; fallo de email NO revierte el pedido
- [ ] 4.4 `backend/dependencies.py`: sustituir `get_db` por inyección del cliente DynamoDB

## 5. Datos demo (seed)

- [ ] 5.1 Crear `seed_dynamodb.py` idempotente con dataset por defecto de ropa/tenis (variantes talla/color) + admin
- [ ] 5.2 Soportar dataset alternativo (otro vertical) sin cambios de código
- [ ] 5.3 Eliminar `seed_products.py` y dependencia de datos relacionales

## 6. Frontend (S3/CloudFront + mejoras)

- [ ] 6.1 `frontend/js/api.js`: base URL de la API por configuración (no localhost hardcodeado)
- [ ] 6.2 Cargar branding/categorías/tema desde `GET /api/config` (CSS Custom Properties, sin frameworks)
- [ ] 6.3 Navegación por categorías data-driven (`js/pages/catalog.js`)
- [ ] 6.4 Selector de variante genérico + bloqueo de variante agotada (`product.html`, `js/pages/product.js`)
- [ ] 6.5 Galería de producto y estados de carga/vacío/error en catálogo y detalle
- [ ] 6.6 Accesibilidad (labels, aria, contraste) y responsive en 375/768/1280px
- [ ] 6.7 Bucket S3 + CloudFront (OAC) en SAM; publicar el frontend

## 7. Revisar y actualizar pruebas (OBLIGATORIO)

- [ ] 7.1 Migrar `tests/conftest.py` de SQLite in-memory a DynamoDB Local / `moto` (crear tabla+GSIs por test)
- [ ] 7.2 Actualizar `tests/test_auth.py`, `test_products.py`, `test_cart.py`, `test_orders.py`, `test_admin.py` al modelo DynamoDB
- [ ] 7.3 Añadir pruebas: variantes/atributos, `store-configuration`, checkout transaccional, cargador idempotente

## 8. Ejecutar pruebas y verificar estado (OBLIGATORIO — EL AGENTE EJECUTA)

- [ ] 8.1 `poetry run ruff check .` sin errores
- [ ] 8.2 `poetry run pytest` (suite completa contra DynamoDB Local/moto) en verde
- [ ] 8.3 Capturar conteos antes/después y restaurar estado de datos si las pruebas lo mutan
- [ ] 8.4 Crear reporte en `specs/migrate-to-serverless-aws/reports/AAAA-MM-DD-step-8-pruebas-y-verificacion.md`

## 9. Verificación manual E2E (OBLIGATORIO — EL AGENTE EJECUTA)

- [ ] 9.1 Levantar `sam local start-api` + DynamoDB Local y sembrar el dataset
- [ ] 9.2 Probar endpoints clave (`curl`): `/api/health`, `/api/config`, `/api/products` (filtros/paginación), `/api/products/{id}`
- [ ] 9.3 Flujo cliente E2E: navegar → filtrar → detalle → elegir variante → carrito → checkout → confirmación + email (SES) → historial
- [ ] 9.4 Flujo admin E2E: login admin → dashboard → crear/editar producto con variantes → cambiar estado de pedido; verificar 403 sin rol admin
- [ ] 9.5 Verificar checkout sin stock (transacción falla, sin pedido ni descuento) y carrito visitante→login
- [ ] 9.6 Restaurar estado de datos sembrados; documentar comandos y resultados en el reporte

## 10. Despliegue en AWS (tier 0)

- [ ] 10.1 `sam build` y `sam deploy` a un entorno `dev`; capturar outputs (URL API y CloudFront)
- [ ] 10.2 Verificar identidad de remitente SES (sandbox) y variables de entorno de producción
- [ ] 10.3 Smoke test del flujo de compra contra el stack desplegado
- [ ] 10.4 Revisar el panel de billing/alarma para confirmar costo ~0

## 11. Actualizar documentación (OBLIGATORIO)

- [ ] 11.1 Crear `docs/aws-serverless-standards.md` (arquitectura, single-table design, SAM, SES, IAM, tier 0)
- [ ] 11.2 Actualizar `README.md` y `PLAN.md` (arquitectura serverless, comandos de deploy/seed/local)
- [ ] 11.3 Actualizar `docs/backend-standards.md` (datos DynamoDB en vez de SQLAlchemy/Alembic; throttling/email)
- [ ] 11.4 Verificar consistencia documental: 0 referencias rotas, una fuente canónica por dato
