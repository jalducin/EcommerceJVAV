## ADDED Requirements

### Requirement: Subida de imágenes de producto vía URL prefirmada

El backend SHALL exponer `POST /api/admin/uploads/presign` (guardado por `require_admin`) que recibe
`{ filename, content_type }` y devuelve `{ upload_url, public_url, key }`, donde `upload_url` es una URL
**PUT prefirmada** de S3 de expiración corta hacia el prefijo `media/` del bucket de frontend, y
`public_url` es la URL pública servida por CloudFront. El endpoint SHALL aceptar únicamente
`content_type` de imagen (`image/jpeg`, `image/png`, `image/webp`, `image/avif`) y rechazar cualquier otro
con 422. El navegador SHALL subir el archivo directamente a `upload_url` y luego persistir `public_url` en
las imágenes del producto. El Lambda SHALL tener permiso de mínimo privilegio `s3:PutObject` solo sobre
`media/*`.

#### Scenario: Solicitar una URL prefirmada para una imagen válida

- **WHEN** el admin solicita `POST /api/admin/uploads/presign` con un `content_type` de imagen permitido
- **THEN** el backend responde 200 con `upload_url`, `public_url` y `key` bajo el prefijo `media/`
- **AND** el navegador puede subir el archivo con `PUT upload_url` y obtener una respuesta 200 de S3

#### Scenario: Rechazo de tipo de archivo no permitido

- **WHEN** el admin solicita una URL prefirmada con un `content_type` que no es de imagen
- **THEN** el backend responde 422 y no genera ninguna URL prefirmada
- **AND** la UI muestra que el tipo de archivo no está permitido

#### Scenario: Subida no autenticada o sin rol admin

- **WHEN** un usuario sin sesión o sin rol admin solicita `POST /api/admin/uploads/presign`
- **THEN** el backend responde 401 o 403 según corresponda
- **AND** no se genera ninguna URL prefirmada
