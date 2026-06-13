# api-swagger Specification

## Purpose
TBD - created by archiving change sprint-8-runbooks-tests-swagger. Update Purpose after archive.
## Requirements
### Requirement: Exposición de Swagger UI y esquema OpenAPI

El sistema SHALL exponer la documentación interactiva en `/docs` (Swagger UI) y el esquema en
`/openapi.json`, generados por FastAPI con los metadatos de la aplicación (título, versión, descripción y
`openapi_tags`) configurados en `backend/app.py`.

#### Scenario: Swagger UI disponible

- **WHEN** se solicita `GET /docs`
- **THEN** responde la interfaz Swagger UI que lista todos los servicios de la API
- **AND** `GET /openapi.json` devuelve un esquema OpenAPI válido con título, versión y tags de la aplicación

#### Scenario: El esquema cubre todos los routers

- **WHEN** se inspecciona `/openapi.json`
- **THEN** incluye todas las rutas de auth, config, products, cart, orders, admin y health
- **AND** cada ruta declara sus métodos, parámetros y modelo de respuesta

### Requirement: Enriquecimiento de cada router

Cada router HTTP (`auth`, `config`, `catalog`, `cart`, `orders`, `admin`) MUST declarar en sus operaciones
`summary`, `description`, `tags`, `response_model` y las `responses` de error relevantes (401/403/404/422),
de modo que la documentación generada sea autoexplicativa por operación.

#### Scenario: Una operación documenta su contrato completo

- **WHEN** se abre una operación cualquiera en Swagger UI (p. ej. `POST /api/orders/checkout`)
- **THEN** muestra summary, description, tag, modelo de respuesta y las respuestas de error posibles
- **AND** los códigos de error documentados coinciden con el comportamiento real del endpoint

#### Scenario: Operaciones protegidas indican su seguridad

- **WHEN** se documenta un endpoint que exige autenticación o rol admin
- **THEN** la operación indica el esquema de seguridad (bearer JWT) y las respuestas 401/403
- **AND** los endpoints públicos (config, listado de catálogo, health) no exigen autenticación en el esquema

### Requirement: Agrupación por tags coherentes

El esquema OpenAPI SHALL agrupar las operaciones en tags coherentes (auth, config, products, cart, orders,
admin, health) con una descripción por tag definida en `openapi_tags`, para que Swagger UI presente los
servicios organizados.

#### Scenario: Tags presentes y descritos

- **WHEN** se carga Swagger UI
- **THEN** las operaciones aparecen agrupadas bajo sus tags con la descripción de cada tag
- **AND** ninguna operación queda sin tag

### Requirement: Contratos de conectores no-HTTP documentados

El proyecto MUST documentar el contrato de las integraciones que no son endpoints HTTP (conectores de
`backend/integrations/connectors/` y el framework de integración) en `docs/integrations-standards.md`:
capacidades declaradas, dirección de sync, payloads canónicos de entrada/salida y mapeo de IDs
externos↔canónicos.

#### Scenario: Contrato de un conector documentado

- **WHEN** se consulta `docs/integrations-standards.md` para un conector
- **THEN** describe sus capacidades, dirección de sync y la forma canónica que produce/consume
- **AND** documenta cómo se mapean los IDs externos a los canónicos

#### Scenario: Cobertura de todos los conectores

- **WHEN** se revisa la documentación de integraciones
- **THEN** existe una entrada de contrato por cada conector presente en `backend/integrations/connectors/`
- **AND** los conectores diferidos por deuda técnica se documentan igualmente, marcados como diferidos

### Requirement: Seguridad de la documentación publicada

La documentación publicada (`/docs` y `/openapi.json`) MUST evitar exponer secretos: los ejemplos no
contienen credenciales reales y, en producción, `/docs` y `/openapi.json` se deshabilitan o se protegen
salvo flag explícito; en entornos no productivos quedan disponibles.

#### Scenario: Sin secretos en el esquema

- **WHEN** se inspecciona `/openapi.json` y los ejemplos de la Swagger UI
- **THEN** no aparecen claves, tokens ni credenciales reales
- **AND** en producción la documentación está deshabilitada o protegida salvo que un flag la habilite explícitamente

### Requirement: OpenAPI servido bajo el prefijo del stage

La documentación OpenAPI SHALL cargarse correctamente cuando la API se sirve bajo un stage de
API Gateway (p. ej. `/dev`): Swagger UI SHALL solicitar el esquema en `/<stage>/api/openapi.json`
mediante el `root_path` de la app, evitando el 404 al cargar la definición.

#### Scenario: Swagger UI carga el esquema con stage

- **WHEN** se abre `/<stage>/api/docs`
- **THEN** Swagger UI solicita `/<stage>/api/openapi.json` y responde `200`
- **AND** la definición de la API se carga sin error

