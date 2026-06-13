## ADDED Requirements

### Requirement: Endpoint de métricas del dashboard

El sistema SHALL exponer `GET /api/admin/dashboard`, protegido con `require_admin`, que devuelve las métricas del día: ventas (importe y conteo) incluyendo pedidos de canales externos, número de pedidos pendientes, productos con stock bajo y la salud de los conectores. El endpoint MUST responder 401 sin token y 403 sin rol admin.

#### Scenario: Admin consulta el dashboard

- **WHEN** un admin autenticado solicita `GET /api/admin/dashboard`
- **THEN** la respuesta 200 incluye ventas del día, pedidos pendientes, stock bajo y salud de conectores
- **AND** las ventas agregan tanto pedidos del storefront como de canales externos

#### Scenario: Acceso sin rol admin

- **WHEN** un usuario sin rol admin solicita `GET /api/admin/dashboard`
- **THEN** el backend responde 403
- **AND** no expone ninguna métrica

### Requirement: Ventas del día incluyen pedidos de canales

El cálculo de ventas del día SHALL sumar los pedidos del storefront y los pedidos canónicos del hub de pedidos unificado provenientes de canales externos, sin contar dos veces un pedido ya consolidado.

#### Scenario: Ventas combinan storefront y canal

- **WHEN** en el día hay pedidos del storefront y pedidos ingresados de un canal externo
- **THEN** el total de ventas del día suma ambos orígenes
- **AND** un pedido de canal ya consolidado no se cuenta por duplicado

### Requirement: Indicadores de pedidos pendientes y stock bajo

El dashboard SHALL reportar el conteo de pedidos en estado pendiente y la lista de productos cuyo stock está por debajo del umbral configurado, para que el admin priorice su operación.

#### Scenario: Hay pedidos pendientes y stock bajo

- **WHEN** existen pedidos pendientes y variantes por debajo del umbral de stock
- **THEN** el dashboard muestra el conteo de pendientes y la lista de productos con stock bajo
- **AND** al no haber ninguno muestra estados vacíos en cero, no un error

### Requirement: Salud de conectores en el dashboard

El dashboard SHALL incluir un resumen de la salud de los conectores (conectores habilitados, con fallos o con mensajes en DLQ) tomado de la observabilidad del Sprint 1, degradando con elegancia si aún no hay conectores habilitados.

#### Scenario: Sin conectores habilitados

- **WHEN** ningún conector está habilitado todavía
- **THEN** el resumen de salud aparece vacío (cero conectores) sin error
- **AND** el resto del dashboard se renderiza normalmente
