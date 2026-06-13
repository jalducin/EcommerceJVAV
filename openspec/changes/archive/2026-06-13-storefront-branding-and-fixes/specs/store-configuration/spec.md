## ADDED Requirements

### Requirement: Marca renderizada desde la configuración en el frontend

El frontend SHALL renderizar el nombre/marca de la tienda a partir de `GET /api/config`
(elementos `data-store-name`), sin texto fijo de un vertical específico en el hero ni el
footer. La marca por defecto es "JV Market" y cambiarla es solo configuración.

#### Scenario: La tienda muestra la marca de la configuración

- **WHEN** se carga el storefront con la configuración por defecto
- **THEN** el hero/navbar/footer muestran "JV Market"
- **AND** no aparece copy fijo de herramientas/acero de un vertical concreto
