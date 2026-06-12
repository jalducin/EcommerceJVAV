## Context

Sobre la base serverless del Sprint 0 (Lambda, DynamoDB single-table, API Gateway, SAM) construimos el
núcleo que permitirá conectar canales de venta, CRM/ERP y POS. El reto no es un proveedor concreto sino el
**patrón**: muchos proveedores con auth, modelos y límites distintos, sincronización de inventario sin
sobreventa, e ingesta de pedidos deduplicada. La solución es un **anti-corruption layer** con modelo
canónico + adapters, y un pipeline asíncrono idempotente.

## Goals / Non-Goals

**Goals:**
- Modelo canónico provider-agnostic y mapeo de IDs externos↔canónicos.
- Framework de adapters con capacidades declaradas y registro por configuración.
- Credenciales en Secrets Manager + OAuth/refresh.
- Webhooks validados y desacoplados (encolado) + motor async idempotente con DLQ, backoff y rate limiting.
- Inventario fuente única con anti-sobreventa y propagación a canales; hub de pedidos unificado.
- Observabilidad: logs estructurados, métricas y estado por conector, gestión de DLQ.
- Conector **mock** de referencia para validar el framework sin proveedor real.

**Non-Goals:**
- Conectores de proveedores reales (Sprints 2-6).
- Multi-tenant real (varias empresas aisladas); la configuración es por despliegue.
- UI de administración avanzada (se expone estado; el panel se enriquece después).

## Decisions

### Decisión 1: Anti-corruption layer (modelo canónico + adapters)

Cada conector implementa una interfaz de adapter y traduce a/desde el modelo canónico. Alternativa
(integraciones punto a punto sin canónico) descartada: O(n²) acoplamientos y sobreventa difícil de evitar.
El canónico reutiliza el producto/variantes business-agnostic del Sprint 0.

### Decisión 2: Mapeo de IDs como ítems en DynamoDB

Correspondencia canónico↔externo por conector como ítems en la tabla single-table:

```
PK = MAP#<connector>#<entity_type>      SK = EXT#<external_id>     -> canonical_id   (externo→canónico)
PK = ENTITY#<entity_type>#<canonical_id> SK = MAP#<connector>      -> external_id     (canónico→externo)
```

Doble escritura para resolver en ambos sentidos con `GetItem` O(1). Idempotencia de ingesta se apoya aquí.

### Decisión 3: Pipeline async EventBridge + SQS + DLQ; workers Lambda

Webhooks y cambios canónicos publican eventos a EventBridge; reglas enrutan a colas SQS por dominio
(inventario, pedidos, catálogo) con DLQ. Workers Lambda consumen. Alternativa (procesar en el request del
webhook) descartada: timeouts, pérdida de eventos y acoplamiento. El webhook responde `2xx` y encola.

### Decisión 4: Idempotencia por clave de evento

Cada evento lleva una **idempotency key** (p. ej. `connector#entity#external_id#event_id`). Antes de
aplicar efectos, el worker registra/consulta la clave (ítem condicional en DynamoDB con TTL). Reentregas
de SQS y webhooks duplicados se descartan sin efecto.

### Decisión 5: Anti-sobreventa con actualización condicional

El nivel de inventario se descuenta con `UpdateItem` + `ConditionExpression (stock >= qty)`. La carrera
por la última unidad la gana una sola escritura; la otra falla por condición. El checkout del Sprint 0
(TransactWriteItems) se generaliza para que cualquier canal descuente del mismo inventario canónico.

### Decisión 6: Rate limiting por proveedor

Límite por conector configurable (token bucket). Implementación pragmática: contadores con ventana en
DynamoDB o un mecanismo de "delay+reencolado" en SQS. Ante `429`/límite, se difiere (visibility timeout /
reencolado), nunca se descarta.

### Decisión 7: Credenciales en Secrets Manager + OAuth/refresh

Un secreto por conector/tienda. El cliente de cada adapter obtiene el secreto en runtime (con cache corto)
y, para OAuth, refresca tokens al detectar expiración y persiste el nuevo. Nunca en código ni en la tabla
de datos.

### Decisión 8: Conector mock de referencia

Un adapter `mock` que implementa todas las capacidades en memoria/local sirve para validar el framework,
la idempotencia y el anti-sobreventa en tests sin depender de un proveedor real.

## Risks / Trade-offs

- **Consistencia eventual entre canales** → Mitigación: inventario canónico como fuente única + propagación
  async; se documenta la ventana de propagación.
- **Sobreventa por latencia de propagación** → Mitigación: el descuento siempre es contra el canónico
  (condicional); los canales reciben niveles derivados; reconciliación periódica por conector.
- **Diversidad de auth/firmas de webhook** → Mitigación: validación de firma por proveedor encapsulada en
  cada adapter; el núcleo solo orquesta.
- **Veneno en cola (poison messages)** → Mitigación: DLQ + reproceso idempotente; límite de reintentos.
- **Costos AWS (EventBridge/SQS/Secrets Manager)** → bajos en free tier para aprendizaje; Secrets Manager
  tiene costo por secreto: documentar y, si hace falta, usar Parameter Store (SecureString) como alternativa.

## Migration Plan

1. Definir entidades canónicas y la tabla/ítems de mapeo de IDs en DynamoDB y SAM.
2. Interfaz de adapter + registro + capacidades; conector mock.
3. Vault (Secrets Manager) + utilidades OAuth/refresh.
4. Webhook ingress (API Gateway + validación de firma) + publicación a EventBridge.
5. Colas SQS + DLQ + workers Lambda; idempotencia y backoff/rate limiting.
6. Inventario unificado (descuento condicional + propagación) y hub de pedidos (ingesta deduplicada,
   estados de fulfillment).
7. Observabilidad (logs estructurados, métricas, estado por conector, reproceso de DLQ).
8. Verificación E2E con el conector mock (idempotencia, anti-sobreventa, dedupe de pedidos).

**Rollback**: el núcleo es aditivo (no rompe el storefront del Sprint 0). Deshabilitar conectores =
configuración; el comercio directo sigue funcionando sin el pipeline de integración.

## Open Questions

- ¿Secrets Manager vs Parameter Store (SecureString) para minimizar costo en aprendizaje?
- ¿Reconciliación: periódica programada (EventBridge Scheduler) y/o bajo demanda por conector?
- ¿Granularidad del rate limiter: por conector o por (conector, endpoint)?
- ¿Step Functions para sagas de sync complejas, o basta SQS+workers para el alcance actual?
