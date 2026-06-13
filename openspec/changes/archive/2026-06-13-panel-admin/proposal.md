## Why

MetalShop ya tiene API serverless de catálogo, pedidos y conectores multicanal, pero carece de un
**panel de administración** usable por un operador no técnico. Hoy el CRUD de productos, la gestión de
pedidos y la observabilidad de conectores solo se ejercen vía API/CLI. El Sprint 7 entrega la **UI
profesional de administración** sobre el API serverless: login de admin, gestión de productos con
variantes, dashboard de métricas, gestión de pedidos unificados (storefront + canales) y vista de salud
de conectores, con una UI premium sin frameworks JS/CSS, accesible y responsive.

Es la capa de operación humana del hub multicanal: consolida lo que los Sprints 0–6 dejaron como API en
una experiencia única para el administrador de la tienda.

## What Changes

- **UI de login y guard de admin**: la vista de administración exige un usuario con rol `admin`; si no lo
  es, redirige/responde 403. Reusa el JWT y `require_admin` del backend.
- **Gestión de productos con variantes desde la UI**: CRUD completo sobre `/api/products` (atributos
  arbitrarios por variante, validación de categoría contra la config de tienda, soft delete `is_active`).
- **Dashboard de métricas**: ventas del día (incluyendo pedidos de canales externos), pedidos pendientes,
  productos con stock bajo y salud de conectores. Requiere un **nuevo endpoint** `GET /api/admin/dashboard`.
- **Gestión de pedidos unificada**: listar pedidos del storefront y de canales en una sola vista y cambiar
  su estado. Requieren **nuevos endpoints** `GET /api/admin/orders` y cambio de estado.
- **Vista de conectores**: estado de sync por conector (último sync, en cola, DLQ, marcados `deferred`) y
  habilitar/deshabilitar; consume el registro de conectores y la observabilidad del Sprint 1.
- **UI profesional sin frameworks**: tema metálico tomado de `store-config` vía CSS Custom Properties,
  responsive en 375/768/1280, estados de carga/vacío/error y accesibilidad (labels, aria, contraste).

## Capabilities

### New Capabilities

- `admin-auth-ui`: login de admin en la UI y guard de las vistas de administración (403/redirect si el
  usuario no tiene rol admin), reusando el JWT y `require_admin` del backend.
- `admin-product-management`: CRUD de productos con variantes (atributos arbitrarios), validación de
  categoría y soft delete, desde la UI sobre `/api/products`.
- `admin-dashboard`: métricas del día (ventas incluyendo canales, pedidos pendientes, stock bajo, salud de
  conectores) servidas por el nuevo `GET /api/admin/dashboard`.
- `admin-order-management`: listado unificado de pedidos (storefront + canales) y cambio de estado, vía los
  nuevos `GET /api/admin/orders` y endpoint de cambio de estado.
- `admin-connectors-view`: vista de estado de sync por conector (último sync, en cola, DLQ, `deferred`) y
  habilitar/deshabilitar, sobre el registro y la observabilidad del Sprint 1.
- `admin-ui-pro`: UI profesional sin frameworks JS/CSS (tema metálico desde store-config, responsive
  375/768/1280, estados de carga/vacío/error, accesibilidad).

### Modified Capabilities

<!-- No modifica specs vigentes en openspec/specs/. Consume (no modifica) capabilities de Sprints previos:
     serverless-api, store-configuration y dynamodb-persistence (Sprint 0); connector-framework,
     unified-orders e integration-observability (Sprint 1). Los nuevos endpoints admin
     (/api/admin/dashboard, /api/admin/orders y cambio de estado) se especifican aquí como parte de las
     capabilities de este cambio. -->

## Impact

- **Dependencias**: requiere Sprint 0 (`migrate-to-serverless-aws`: API serverless, store-config, DynamoDB,
  rol admin/`require_admin`) y Sprint 1 (`integration-platform-core`: registro de conectores, hub de
  pedidos unificado, observabilidad/estado de sync y DLQ). Las vistas de conectores y el dashboard degradan
  con elegancia si los conectores aún no están habilitados (lista vacía, no error).
- **Backend** (nuevos endpoints admin): `backend/routers/admin.py` (o ampliación de routers existentes) con
  `GET /api/admin/dashboard`, `GET /api/admin/orders` y cambio de estado de pedido; servicios de agregación
  que leen catálogo, hub de pedidos (`integrations/channel_orders.py`), inventario
  (`integrations/inventory.py`) y estado de conectores (`integrations/connector.py` + observabilidad). Todos
  protegidos con `require_admin`.
- **Frontend**: `frontend/admin/*.html` (login, dashboard, productos, pedidos, conectores), `frontend/css/*`
  (tema desde CSS Custom Properties), `frontend/js/admin/*` (Fetch API, JWT en localStorage con refresh,
  estados de carga/error). Sin frameworks JS/CSS.
- **Tests**: pruebas de los nuevos endpoints admin (200 con admin, 401/403 sin admin), de la agregación del
  dashboard y del cambio de estado; pruebas de UI del guard y del CRUD si el proyecto las contempla.
- **Docs**: `docs/frontend-standards.md` (patrones del panel y accesibilidad), contrato de los endpoints
  admin y actualización del `docs/roadmap-plataforma-multicanal.md` (Sprint 7).
- **Seguridad**: ningún endpoint admin sin `require_admin`; sin secretos en el frontend; el guard de UI es
  defensa en profundidad, la autoridad real es el backend.
