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

### Requirement: Almacenamiento de imágenes de producto en el bucket de frontend bajo `media/`

El bucket de frontend SHALL alojar las imágenes de producto subidas por el admin bajo el prefijo `media/`,
servidas por la misma distribución de CloudFront que el sitio (lectura vía OAC). El bucket SHALL declarar
una configuración **CORS** que permita `PUT, GET, HEAD` desde el origen del sitio para habilitar la subida
mediante URL prefirmada desde el navegador. No SHALL crearse un bucket ni una distribución nuevos para las
imágenes (reutilización de la infraestructura existente, tier-0).

#### Scenario: Imagen subida servida por CloudFront

- **WHEN** el admin sube una imagen mediante URL prefirmada al prefijo `media/`
- **THEN** la imagen queda accesible por la URL pública de CloudFront sin configuración adicional
- **AND** el storefront la muestra como cualquier otra imagen de producto

#### Scenario: CORS habilita el PUT prefirmado desde el navegador

- **WHEN** el navegador realiza un `PUT` prefirmado al bucket desde el origen del sitio
- **THEN** la respuesta CORS del bucket permite el método `PUT` y la subida tiene éxito
- **AND** una solicitud desde un origen no permitido es rechazada por CORS

