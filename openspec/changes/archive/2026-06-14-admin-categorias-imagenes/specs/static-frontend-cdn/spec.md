## ADDED Requirements

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
