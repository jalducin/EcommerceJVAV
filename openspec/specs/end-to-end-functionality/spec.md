# end-to-end-functionality Specification

## Purpose
TBD - created by archiving change migrate-to-serverless-aws. Update Purpose after archive.
## Requirements
### Requirement: Flujo de compra del cliente funciona de extremo a extremo

El sistema SHALL permitir completar el flujo de compra del cliente de extremo a extremo con el stack
serverless (desplegado o local con SAM + DynamoDB Local) y datos sembrados: navegar el catálogo →
filtrar por categoría → ver detalle → elegir variante → agregar al carrito → checkout → confirmación de
pedido → correo de confirmación → ver el pedido en el historial.

#### Scenario: Compra completa de un par de tenis

- **WHEN** un cliente navega, abre un tenis, elige talla 42, lo agrega al carrito y completa el checkout
- **THEN** se crea el pedido, se descuenta el stock de esa variante y se muestra la confirmación con número de pedido
- **AND** se envía el correo de confirmación y el pedido aparece en el historial del cliente

#### Scenario: Carrito de visitante migra al iniciar sesión

- **WHEN** un visitante con items en el carrito (localStorage) inicia sesión
- **THEN** el carrito se sincroniza con su carrito en DynamoDB
- **AND** los items quedan disponibles para el checkout autenticado

### Requirement: Flujo de administración funciona de extremo a extremo

El flujo de admin SHALL funcionar: iniciar sesión como admin → ver dashboard con métricas → crear/editar
producto (con variantes) → ver pedidos → cambiar estado de un pedido.

#### Scenario: Admin crea producto y cambia estado de pedido

- **WHEN** un admin crea un producto con variantes y luego cambia un pedido de `pending` a `shipped`
- **THEN** el producto aparece en el catálogo y el dashboard refleja las métricas actualizadas
- **AND** el estado del pedido cambia y es visible para el cliente

#### Scenario: Acceso de admin restringido por rol

- **WHEN** un usuario sin rol admin intenta acceder a un endpoint de administración
- **THEN** la API responde `403 Forbidden`

### Requirement: Verificación ejecutada por el agente

La funcionalidad de extremo a extremo SHALL verificarse ejecutando el flujo (manual o E2E automatizado)
contra el entorno local o desplegado, documentando comandos, resultados y restauración de estado, según
la regla de pasos obligatorios de tasks. NO SHALL marcarse completa sin ejecutar la verificación.

#### Scenario: Reporte de verificación E2E

- **WHEN** se completa la implementación del cambio
- **THEN** existe un reporte en `specs/migrate-to-serverless-aws/reports/` con el flujo ejecutado y sus resultados
- **AND** el estado de datos sembrados queda restaurado tras la verificación

