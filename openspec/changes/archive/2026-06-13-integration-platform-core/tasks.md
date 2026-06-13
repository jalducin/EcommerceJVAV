## 0. Preparación (OBLIGATORIO)

- [ ] 0.1 Crear y cambiar a la feature branch `feature/integration-platform-core` (Step 0 — SIEMPRE primero)
- [ ] 0.2 Leer `openspec/config.yaml`, `docs/integrations-standards.md` (se crea aquí), `docs/aws-serverless-standards.md` y la regla de pasos obligatorios
- [ ] 0.3 Confirmar que el Sprint 0 (`migrate-to-serverless-aws`) está implementado (DynamoDB, SAM, runtime serverless)

## 1. Modelo canónico y mapeo de IDs

- [ ] 1.1 Definir entidades canónicas (Producto, Variante, NivelDeInventario, Pedido, Cliente, Pago, Fulfillment) y schemas Pydantic en `backend/integrations/canonical/`
- [ ] 1.2 Implementar el mapeo de IDs externo↔canónico (doble escritura en DynamoDB) y sus helpers de resolución
- [ ] 1.3 Añadir ítems de mapeo y de estado de sync a la tabla single-table (claves del design)

## 2. Connector framework

- [ ] 2.1 Definir la interfaz de adapter y el enum de capacidades (catálogo, inventario, pedidos, clientes, pagos, fulfillment)
- [ ] 2.2 Implementar el registro de conectores habilitados por configuración
- [ ] 2.3 Implementar el conector **mock** de referencia (todas las capacidades, en memoria/local)
- [ ] 2.4 Vault de credenciales con AWS Secrets Manager + utilidades OAuth y refresh de tokens

## 3. Webhooks + bus async

- [ ] 3.1 Endpoints de webhook (API Gateway) con validación de firma por proveedor (encapsulada en adapter)
- [ ] 3.2 Publicar eventos a EventBridge y enrutar a colas SQS por dominio (inventario, pedidos, catálogo) con DLQ
- [ ] 3.3 Workers Lambda que consumen SQS; respuesta `2xx` inmediata del webhook (procesamiento diferido)
- [ ] 3.4 Idempotencia por clave de evento (ítem condicional en DynamoDB con TTL)
- [ ] 3.5 Reintentos con backoff exponencial y rate limiting por proveedor (diferir, no descartar)

## 4. Inventario y pedidos unificados

- [ ] 4.1 Inventario fuente única: descuento condicional/atómico (anti-sobreventa) generalizando el checkout del Sprint 0
- [ ] 4.2 Propagación async de cambios de stock a conectores que soporten inventario
- [ ] 4.3 Hub de pedidos: ingesta deduplicada por mapeo de IDs (canal de origen + id externo)
- [ ] 4.4 Sincronización de estado de fulfillment canónico↔canal según capacidades del conector

## 5. Observabilidad

- [ ] 5.1 Logs estructurados con correlación por evento (conector, entidad, ids, resultado)
- [ ] 5.2 Métricas y estado de sync por conector (último sync, en cola, fallos, DLQ) consultable por el panel admin
- [ ] 5.3 Inspección y reproceso idempotente de mensajes en la DLQ

## 6. Infraestructura (SAM)

- [ ] 6.1 Añadir a `template.yaml`: EventBridge bus, colas SQS + DLQ, Secrets Manager, rutas de webhook, workers Lambda
- [ ] 6.2 Roles IAM de mínimo privilegio (SQS, EventBridge, Secrets Manager, DynamoDB)
- [ ] 6.3 Ejecución local equivalente (DynamoDB Local + SAM local + colas/eventos simulados o localstack)

## 7. Revisar y actualizar pruebas (OBLIGATORIO)

- [ ] 7.1 Pruebas del framework con el conector mock (capacidades, registro, mapeo de IDs)
- [ ] 7.2 Pruebas de idempotencia (reentrega de eventos, webhooks duplicados) y de anti-sobreventa (carrera por última unidad)
- [ ] 7.3 Pruebas de ingesta deduplicada de pedidos y de propagación de inventario

## 8. Ejecutar pruebas y verificar estado (OBLIGATORIO — EL AGENTE EJECUTA)

- [ ] 8.1 `poetry run ruff check .` sin errores
- [ ] 8.2 `poetry run pytest` (con DynamoDB Local/moto y colas simuladas) en verde
- [ ] 8.3 Reporte en `specs/integration-platform-core/reports/AAAA-MM-DD-step-8-pruebas-y-verificacion.md`

## 9. Verificación manual E2E con conector mock (OBLIGATORIO — EL AGENTE EJECUTA)

- [ ] 9.1 Levantar el stack local; registrar el conector mock
- [ ] 9.2 Simular webhook de pedido (firma válida e inválida) y verificar encolado, idempotencia y creación única
- [ ] 9.3 Simular venta concurrente en dos "canales" mock y verificar que no hay sobreventa ni stock negativo
- [ ] 9.4 Provocar fallos para verificar DLQ y reproceso idempotente; revisar estado de sync del conector
- [ ] 9.5 Restaurar estado de datos; documentar comandos y resultados en el reporte

## 10. Actualizar documentación (OBLIGATORIO)

- [ ] 10.1 Crear `docs/integrations-standards.md` (patrón adapter, modelo canónico, mapeo de IDs, idempotencia, secretos, rate limiting)
- [ ] 10.2 Actualizar `docs/aws-serverless-standards.md` (EventBridge/SQS/DLQ/Secrets Manager) y `docs/roadmap-plataforma-multicanal.md`
- [ ] 10.3 Verificar consistencia documental: 0 referencias rotas, una fuente canónica por dato
