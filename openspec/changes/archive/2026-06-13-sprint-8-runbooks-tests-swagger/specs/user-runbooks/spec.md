## ADDED Requirements

### Requirement: Estructura común de cada runbook

Cada runbook operativo MUST documentar, en este orden, las secciones: **Objetivo**, **Precondiciones**,
**Pasos**, **Verificación** y **Troubleshooting**. Los runbooks viven en `docs/runbooks/` como fuente
canónica, con un archivo por tipo de usuario y un índice `README.md` que los enlaza.

#### Scenario: Un runbook tiene todas las secciones obligatorias

- **WHEN** se abre cualquier runbook en `docs/runbooks/`
- **THEN** contiene las secciones Objetivo, Precondiciones, Pasos, Verificación y Troubleshooting en ese orden
- **AND** el índice `docs/runbooks/README.md` enlaza a los cuatro runbooks por tipo de usuario

#### Scenario: Cada paso es verificable

- **WHEN** un usuario sigue la sección Pasos de un runbook
- **THEN** la sección Verificación describe cómo confirmar que el resultado esperado ocurrió
- **AND** la sección Troubleshooting lista al menos un fallo común con su causa y acción correctiva

### Requirement: Runbook del visitante

El sistema SHALL incluir un runbook para el **visitante** que cubra navegar y buscar el catálogo sin sesión,
documentando objetivo, precondiciones, pasos, verificación y troubleshooting de esas tareas.

#### Scenario: Visitante navega y busca el catálogo

- **WHEN** un visitante sigue el runbook para listar productos y buscar/filtrar por categoría
- **THEN** el runbook describe los pasos sobre `GET /api/products` (paginación, búsqueda, filtro de categoría)
- **AND** la verificación confirma que se muestran productos activos sin requerir sesión
- **AND** el troubleshooting cubre catálogo vacío y errores de carga del storefront

### Requirement: Runbook del cliente

El sistema SHALL incluir un runbook para el **cliente** que cubra registro/login, gestión del carrito,
checkout y consulta de pedidos, documentando objetivo, precondiciones, pasos, verificación y troubleshooting.

#### Scenario: Cliente se registra, compra y consulta su pedido

- **WHEN** un cliente sigue el runbook para registrarse o iniciar sesión, agregar ítems al carrito y hacer checkout
- **THEN** el runbook describe los pasos sobre `/api/auth` (register/login/refresh), `/api/cart` (items/sync) y `/api/orders/checkout`
- **AND** la verificación confirma la creación del pedido y su aparición en `GET /api/orders`
- **AND** el troubleshooting cubre token expirado, carrito desincronizado y checkout fallido

### Requirement: Runbook del administrador

El sistema SHALL incluir un runbook para el **administrador** que cubra la gestión de catálogo con variantes,
de pedidos, del dashboard y de conectores, documentando objetivo, precondiciones, pasos, verificación y
troubleshooting.

#### Scenario: Administrador gestiona catálogo, pedidos, dashboard y conectores

- **WHEN** un administrador sigue el runbook para crear/editar/desactivar productos con variantes, revisar el dashboard, gestionar pedidos y operar conectores
- **THEN** el runbook describe los pasos sobre el panel admin y los endpoints `/api/products` y `/api/admin/*`, con la precondición de tener rol admin
- **AND** la verificación confirma los cambios reflejados (producto activo/inactivo, estado de pedido, métricas, estado de conector)
- **AND** el troubleshooting cubre acceso 403 sin rol admin, validación de categoría y conector sin habilitar

### Requirement: Runbook del operador/DevOps

El sistema SHALL incluir un runbook para el **operador/DevOps** que cubra el despliegue con SAM, el seed de
datos, la rotación de secretos del vault, el teardown y la lectura de logs/DLQ, documentando objetivo,
precondiciones, pasos, verificación y troubleshooting.

#### Scenario: Operador despliega, siembra y opera la plataforma

- **WHEN** un operador sigue el runbook para desplegar con SAM, sembrar datos demo y verificar el stack
- **THEN** el runbook describe los pasos de `sam build`/`sam deploy`, seed, salida esperada del stack y comprobación de `GET /api/health`
- **AND** la verificación confirma el stack desplegado y respondiendo
- **AND** el troubleshooting cubre fallos de despliegue, permisos IAM y rollback

#### Scenario: Operador rota secretos del vault y revisa la DLQ

- **WHEN** un operador sigue el runbook para rotar un secreto del vault de credenciales y revisar mensajes en la DLQ
- **THEN** el runbook describe los pasos de rotación de secretos y de lectura de logs estructurados y de la cola de mensajes muertos (DLQ)
- **AND** la verificación confirma que el conector sigue autenticando tras la rotación y que la DLQ se inspecciona sin reprocesar a ciegas
- **AND** el troubleshooting cubre secreto inválido tras rotar, acumulación en DLQ y teardown seguro del stack
