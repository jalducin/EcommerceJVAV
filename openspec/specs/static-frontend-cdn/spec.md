# static-frontend-cdn Specification

## Purpose
TBD - created by archiving change migrate-to-serverless-aws. Update Purpose after archive.
## Requirements
### Requirement: Frontend servido desde S3 a través de CloudFront

El frontend estático (HTML/CSS/JS) SHALL alojarse en un bucket S3 y servirse a través de una
distribución CloudFront. El frontend NO SHALL servirse desde la Lambda (`StaticFiles` se elimina del
backend de producción).

#### Scenario: Carga de la página principal

- **WHEN** un navegador solicita la raíz del dominio de CloudFront
- **THEN** CloudFront sirve `index.html` desde S3
- **AND** los assets (css/js) se cargan desde CloudFront

#### Scenario: El bucket S3 no es público directamente

- **WHEN** se intenta acceder al bucket S3 por su URL directa
- **THEN** el acceso está restringido (p. ej. Origin Access Control), sirviéndose solo vía CloudFront

### Requirement: El frontend consume la API por su URL de API Gateway

El frontend SHALL apuntar sus llamadas a la URL pública de la API (API Gateway/CloudFront) mediante
configuración (no hardcodeada a `localhost`). Las llamadas cross-origin SHALL resolverse con la
configuración CORS del backend.

#### Scenario: Llamada del frontend a la API en producción

- **WHEN** el frontend desplegado hace `GET /api/products`
- **THEN** la petición llega a API Gateway y la respuesta incluye los encabezados CORS correctos
- **AND** el catálogo se renderiza con los productos recibidos

