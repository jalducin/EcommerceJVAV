## ADDED Requirements

### Requirement: Documentación OpenAPI protegida o deshabilitada

La documentación OpenAPI (Swagger UI, ReDoc y `openapi.json`) NO SHALL ser pública. Cuando hay
credenciales configuradas, el acceso SHALL requerir HTTP Basic auth; cuando no las hay, los
endpoints de documentación SHALL estar deshabilitados (responder 404). Las credenciales SHALL
provenir del entorno, nunca del repositorio.

#### Scenario: Acceso sin credenciales es rechazado

- **WHEN** alguien abre `/api/docs` o `/api/openapi.json` sin credenciales válidas (con docs habilitados)
- **THEN** la respuesta es `401` con `WWW-Authenticate: Basic`
- **AND** no se expone el esquema de la API

#### Scenario: Acceso con credenciales válidas

- **WHEN** se accede a `/api/docs` con el usuario y contraseña correctos
- **THEN** Swagger UI carga y obtiene `openapi.json` (también protegido)

#### Scenario: Docs deshabilitados sin contraseña configurada

- **WHEN** no hay `DOCS_PASSWORD` configurada y se abre `/api/docs`
- **THEN** la respuesta es `404` (documentación deshabilitada, seguro por defecto)
