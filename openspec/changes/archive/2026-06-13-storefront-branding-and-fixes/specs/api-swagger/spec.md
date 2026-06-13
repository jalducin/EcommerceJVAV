## ADDED Requirements

### Requirement: OpenAPI servido bajo el prefijo del stage

La documentación OpenAPI SHALL cargarse correctamente cuando la API se sirve bajo un stage de
API Gateway (p. ej. `/dev`): Swagger UI SHALL solicitar el esquema en `/<stage>/api/openapi.json`
mediante el `root_path` de la app, evitando el 404 al cargar la definición.

#### Scenario: Swagger UI carga el esquema con stage

- **WHEN** se abre `/<stage>/api/docs`
- **THEN** Swagger UI solicita `/<stage>/api/openapi.json` y responde `200`
- **AND** la definición de la API se carga sin error
