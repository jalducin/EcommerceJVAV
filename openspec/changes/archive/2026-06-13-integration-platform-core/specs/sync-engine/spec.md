## ADDED Requirements

### Requirement: Orquestación asíncrona con cola y dead-letter

El motor de sincronización SHALL ejecutar los trabajos de sync de forma asíncrona mediante un bus de
eventos (EventBridge) y colas (SQS) con **dead-letter queue (DLQ)**. Un trabajo que falle de forma
repetida SHALL terminar en la DLQ sin bloquear el resto del procesamiento.

#### Scenario: Trabajo fallido va a la DLQ tras agotar reintentos

- **WHEN** un trabajo de sync falla más allá del máximo de reintentos
- **THEN** el mensaje se mueve a la DLQ
- **AND** queda registrado para inspección sin detener otros trabajos

### Requirement: Procesamiento idempotente

El procesamiento de eventos y trabajos SHALL ser **idempotente**: procesar el mismo evento más de una vez
(reentrega de SQS, webhook duplicado) NO SHALL producir efectos duplicados (pedidos repetidos, doble
descuento de inventario).

#### Scenario: Webhook de pedido reentregado no duplica

- **WHEN** el mismo evento de pedido se entrega dos veces
- **THEN** el pedido canónico se crea o actualiza una sola vez
- **AND** el inventario se descuenta una sola vez

### Requirement: Reintentos con backoff y rate limiting por proveedor

Las llamadas salientes a proveedores SHALL aplicar **reintentos con backoff exponencial** ante errores
transitorios y **rate limiting por proveedor** para respetar sus límites de API. Al alcanzar el límite, el
sistema SHALL diferir (no descartar) el trabajo.

#### Scenario: Rate limit del proveedor difiere el trabajo

- **WHEN** un proveedor responde `429` o se alcanza el límite local configurado
- **THEN** el sistema aplica backoff y reintenta más tarde
- **AND** no descarta el trabajo ni satura al proveedor

#### Scenario: Error transitorio se reintenta

- **WHEN** una llamada falla con un error transitorio (5xx/timeout)
- **THEN** se reintenta con backoff exponencial hasta el máximo configurado
- **AND** si persiste, el trabajo va a la DLQ
