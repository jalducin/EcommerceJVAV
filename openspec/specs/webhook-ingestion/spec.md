# webhook-ingestion Specification

## Purpose
TBD - created by archiving change integration-platform-core. Update Purpose after archive.
## Requirements
### Requirement: Recepción y validación de webhooks entrantes

El sistema SHALL exponer endpoints de webhook (API Gateway → Lambda) para recibir eventos de proveedores.
Cada webhook SHALL validar su **firma/autenticidad** según el proveedor antes de procesarse; los eventos
con firma inválida SHALL rechazarse con `401`.

#### Scenario: Webhook con firma válida se acepta

- **WHEN** llega un webhook con firma válida del proveedor
- **THEN** el sistema responde `2xx` rápidamente
- **AND** encola el evento para procesamiento asíncrono

#### Scenario: Webhook con firma inválida se rechaza

- **WHEN** llega un webhook con firma inválida o ausente
- **THEN** el sistema responde `401`
- **AND** no encola ni procesa el evento

### Requirement: Encolado para procesamiento asíncrono

La recepción del webhook SHALL desacoplarse de su procesamiento: el endpoint SHALL responder de inmediato
y delegar el trabajo a una cola. El procesamiento pesado NO SHALL ejecutarse de forma síncrona dentro del
request del webhook.

#### Scenario: Respuesta rápida y procesamiento diferido

- **WHEN** se recibe un webhook válido de un pedido nuevo
- **THEN** el endpoint responde `2xx` sin procesar el pedido en línea
- **AND** un worker consume el evento desde la cola y lo procesa

