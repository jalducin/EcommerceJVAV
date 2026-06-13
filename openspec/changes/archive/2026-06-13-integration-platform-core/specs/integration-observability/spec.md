## ADDED Requirements

### Requirement: Logs estructurados y trazabilidad por trabajo

El sistema SHALL emitir logs estructurados para cada trabajo de sincronización e ingesta, incluyendo
conector, entidad, id canónico/externo y resultado. Los logs SHALL permitir trazar un evento desde su
recepción hasta su efecto (o su llegada a la DLQ).

#### Scenario: Trazar un pedido desde el webhook hasta su creación

- **WHEN** un pedido entra por webhook y se procesa
- **THEN** los logs registran recepción, encolado, procesamiento y resultado con sus identificadores
- **AND** es posible correlacionar todos los pasos del mismo evento

### Requirement: Métricas y estado de sincronización por conector

El sistema SHALL exponer métricas y un **estado de sincronización por conector** (último sync correcto,
trabajos en cola, fallos, mensajes en DLQ). El estado SHALL ser consultable para el panel de
administración.

#### Scenario: Estado de un conector con fallos

- **WHEN** un conector acumula trabajos en la DLQ
- **THEN** su estado de sync refleja los fallos y el conteo en DLQ
- **AND** el panel admin puede mostrar la salud del conector

### Requirement: Gestión de dead-letter

Los mensajes en la DLQ SHALL poder inspeccionarse y **reprocesarse** (reintento manual) una vez resuelta
la causa, sin perder el evento original.

#### Scenario: Reproceso de un mensaje de la DLQ

- **WHEN** se corrige la causa de fallo y se reprocesa un mensaje de la DLQ
- **THEN** el evento se procesa de forma idempotente
- **AND** no genera efectos duplicados
