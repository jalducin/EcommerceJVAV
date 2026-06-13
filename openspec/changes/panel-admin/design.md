## Context

Sprint 7 del roadmap. Los Sprints 0–6 dejaron el hub multicanal operable solo por API/CLI. Este cambio
añade la **UI de administración profesional** sobre el API serverless existente, más los **endpoints admin**
que la UI necesita y que aún no existen (`GET /api/admin/dashboard`, `GET /api/admin/orders` y el cambio de
estado de pedido). El CRUD de productos ya existe en `/api/products` con `require_admin`; el panel lo
consume. La autenticación reusa el JWT y `require_admin` del Sprint 0.

## Goals / Non-Goals

**Goals:**
- Panel admin completo: login + guard, CRUD de productos con variantes, dashboard, gestión de pedidos
  unificados y vista de conectores.
- UI profesional sin frameworks JS/CSS, tema desde store-config, responsive 375/768/1280, accesible.
- Nuevos endpoints admin de agregación (dashboard) y de operación de pedidos, todos con `require_admin`.

**Non-Goals:**
- Gestión de usuarios/roles desde la UI (alta de admins se hace por seed/backend).
- Reprocesar la DLQ desde la UI (la observabilidad del Sprint 1 lo cubre; aquí solo se muestra el estado).
- Reportería/BI avanzada más allá de las métricas del día del dashboard.

## Decisions

### Decisión 1: Reusar el CRUD existente de `/api/products`
El catálogo ya expone CRUD con `require_admin`, validación de categoría y soft delete (`DELETE` →
`is_active=false`). El panel lo consume tal cual; no se duplica lógica de negocio en la UI. Alternativa
(endpoints admin de producto nuevos) descartada por redundante.

### Decisión 2: Nuevos endpoints admin en `backend/routers/admin.py`
Se agrupan los endpoints de agregación y operación admin (`GET /api/admin/dashboard`, `GET /api/admin/orders`,
cambio de estado) en un router dedicado, todos protegidos con `require_admin`. La agregación lee catálogo,
hub de pedidos (`integrations/channel_orders.list_orders`), inventario (`integrations/inventory`) y el
registro/observabilidad de conectores. La lógica vive en servicios, no en el router (estándar del proyecto).

### Decisión 3: Pedidos unificados = storefront + hub de canales
`GET /api/admin/orders` combina los pedidos del storefront (GSI3 de pedidos por estado) con los pedidos
canónicos del hub (`channel_orders`), normalizando al mismo shape con `channel` de origen. Anti-duplicado:
un pedido de canal consolidado vive solo en el hub, no se recuenta.

### Decisión 4: Guard de UI como defensa en profundidad
El guard en el frontend (redirige/oculta si no hay rol admin) mejora la UX, pero la autoridad real es
`require_admin` en el backend (403). La UI nunca confía en el rol del lado del cliente para autorizar datos.

### Decisión 5: Tema y branding data-driven, sin frameworks
El panel toma tokens de tema de `GET /api/config` y los aplica vía CSS Custom Properties (igual que el
storefront del Sprint 0). HTML5 + CSS3 + JS vanilla; Fetch API; JWT en localStorage con refresh automático.

## Risks / Trade-offs

- **Doble fuente de pedidos (storefront + hub)** → normalizar a un shape único y deduplicar por origen;
  pruebas con ambos orígenes activos.
- **Costo de agregación del dashboard en DynamoDB** → consultas acotadas por GSI (pedidos por estado/fecha)
  y scan acotado solo donde sea inevitable (stock bajo); cachear en memoria de la invocación si hace falta.
- **Guard solo en cliente sería inseguro** → mitigado: backend siempre exige `require_admin`.
- **Conectores aún no habilitados** → la vista y el dashboard degradan a estado vacío, no error.

## Migration Plan

1. Backend: router admin con `GET /api/admin/dashboard`, `GET /api/admin/orders` y cambio de estado;
   servicios de agregación; pruebas (200 admin / 401 sin token / 403 sin rol).
2. Frontend: login + guard; vistas de productos (CRUD), dashboard, pedidos y conectores; tema desde config;
   estados de carga/vacío/error y accesibilidad.
3. Verificación E2E del flujo admin completo contra el stack serverless con datos sembrados.

## Open Questions

- ¿El umbral de stock bajo se define en `store-config` o como constante del backend? (Preferencia:
  store-config para mantener business-agnostic.)
- ¿El cambio de estado de pedido de un canal externo debe propagarse al canal (fulfillment) en este sprint,
  o solo actualizar el estado canónico? (Propuesta: solo canónico aquí; propagación queda para los sprints
  de canal.)
