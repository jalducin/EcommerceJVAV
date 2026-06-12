## Why

Para soportar venta multicanal + CRM + POS necesitamos un **núcleo de integración** antes de conectar
cualquier proveedor. Sin un modelo canónico y un framework de conectores, cada integración se volvería
código ad-hoc acoplado, con sobreventa entre canales y pedidos dispersos. Este cambio construye la
columna vertebral: modelo canónico, framework de adapters, credenciales seguras, webhooks, motor de
sincronización async, inventario y pedidos unificados, y observabilidad. Es el **Sprint 1** del roadmap y
prerrequisito de los Sprints 2-6.

## What Changes

- Se define un **modelo canónico** business-agnostic: Producto, Variante, NivelDeInventario, Pedido,
  Cliente, Pago, Fulfillment; independiente de cualquier proveedor.
- Se introduce un **connector framework**: interfaz de adapter con capacidades declaradas
  (catálogo/inventario/pedidos/clientes/pagos), registro de conectores y **mapeo de IDs**
  externos↔canónicos (tabla de correspondencias en DynamoDB).
- Las credenciales por conector se guardan en **AWS Secrets Manager**, con soporte de **OAuth** y refresh
  de tokens; nunca en código ni en la tabla de datos.
- Se añade **ingesta de webhooks** (API Gateway → Lambda → validación de firma → encolado) para eventos
  entrantes de proveedores.
- Se añade un **motor de sincronización asíncrono** con EventBridge + SQS + DLQ: jobs idempotentes,
  reintentos con backoff y **rate limiting por proveedor**.
- Se establece el **inventario unificado** como fuente única de verdad con prevención de sobreventa, y un
  **hub de pedidos unificado** que consolida pedidos de todos los canales en el modelo canónico.
- Se añade **observabilidad**: logs estructurados, métricas de sync, estado por conector y manejo de
  dead-letter.
- Se incluye un **conector de referencia mock** para validar el framework sin depender de un proveedor real.

## Capabilities

### New Capabilities
- `canonical-commerce-model`: modelo de dominio canónico (producto, variante, inventario, pedido, cliente,
  pago, fulfillment) independiente de proveedor.
- `connector-framework`: interfaz de adapter, registro de conectores, capacidades, mapeo de IDs y vault de
  credenciales (Secrets Manager + OAuth/refresh).
- `webhook-ingestion`: recepción y validación de webhooks entrantes y su encolado para procesamiento.
- `sync-engine`: orquestación async (EventBridge/SQS/DLQ) con idempotencia, reintentos/backoff y rate
  limiting por proveedor.
- `unified-inventory`: inventario como fuente única de verdad con prevención de sobreventa entre canales.
- `unified-orders`: hub que consolida pedidos de todos los canales en el modelo canónico.
- `integration-observability`: logs, métricas, estado de sync por conector y manejo de dead-letter.

### Modified Capabilities
<!-- Depende del Sprint 0 (migrate-to-serverless-aws). No modifica specs vigentes (aún no archivados). -->

## Impact

- **Backend nuevo**: `backend/integrations/` (modelo canónico, interfaz de adapter, registro, mapeo de IDs,
  vault, motor de sync, conector mock); workers Lambda para consumo de SQS.
- **Datos**: nuevas entidades canónicas y tabla/ítems de **mapeo externo↔canónico** y de **estado de sync**
  en DynamoDB single-table; el inventario pasa a ser fuente única consultable por todos los canales.
- **Infra (SAM)**: EventBridge bus, colas SQS + DLQ, Secrets Manager, rutas de webhook en API Gateway,
  permisos IAM de mínimo privilegio.
- **Dependencias**: +`boto3` (EventBridge/SQS/Secrets Manager), librería HTTP async (p. ej. `httpx`).
- **Tests**: framework de adapter con conector mock; pruebas de idempotencia, anti-sobreventa, mapeo de IDs.
- **Docs**: nuevo `docs/integrations-standards.md` (patrón adapter, idempotencia, mapeo, secretos),
  actualizar `docs/aws-serverless-standards.md` y el roadmap.
- **Dependencia**: requiere el Sprint 0 (`migrate-to-serverless-aws`) implementado.
