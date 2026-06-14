# Design: Gestión de categorías e imágenes de producto

## Contexto

- Las categorías viven en `StoreConfig.categories: list[str]` (DynamoDB, item de config) y se exponen en
  `GET /api/config`. `store_repo.put_config()` ya persiste la config completa.
- El CRUD de productos está en `backend/routers/catalog.py` (`POST/PUT /api/products`, guardado por
  `require_admin`); `ProductCreate.images: list[str]` ya admite varias imágenes. `_validate_category`
  rechaza categorías fuera de `config.categories` con 422.
- El frontend es estático en `FrontendBucket` (S3) servido por `FrontendDistribution` (CloudFront, OAC,
  solo lectura). El Lambda (Mangum) corre el API bajo API Gateway HTTP.

## Decisiones

### 1. Categorías: CRUD mínimo sobre la config existente

Nuevos endpoints admin (en `admin.py`, prefijo `/api/admin`):

- `GET /api/admin/categories` → `list[str]` (lee `config.categories`).
- `POST /api/admin/categories` body `{ "name": str }` → 201, idempotente (si ya existe, 200/no duplica).
- `DELETE /api/admin/categories/{name}` → 204. **Rechaza con 409** si algún producto activo usa la
  categoría (se consulta el catálogo por categoría); así no quedan productos huérfanos.

Persistencia vía `store_repo.put_config()` (lee, muta `categories`, guarda). Validación: nombre no vacío,
trim, sin duplicados (case-insensitive).

### 2. Imágenes: presigned PUT al bucket existente bajo `media/`

Se descarta subir el binario a través del Lambda (límite de payload de API Gateway y costo). En su lugar:

- `POST /api/admin/uploads/presign` body `{ "filename": str, "content_type": str }` → responde
  `{ "upload_url": <url PUT prefirmada>, "public_url": <url CloudFront>, "key": "media/<uuid>.<ext>" }`.
- El Lambda firma con `boto3 s3.generate_presigned_url("put_object", ...)`, expiración corta (p. ej. 300s),
  `ContentType` fijado. Solo `image/*` permitido (jpeg/png/webp/avif); otros → 422.
- El navegador hace `PUT upload_url` con el archivo y luego guarda `public_url` en `images` del producto.
- Las imágenes se sirven por el CloudFront existente (`GetObject` ya permitido por OAC para `/*`).

**Infra (template.yaml):**

- `FrontendBucket.CorsConfiguration`: permitir `PUT, GET, HEAD` desde el origen del sitio
  (`AllowedOrigin`) con headers `*` y `ExposeHeaders: [ETag]`. El presigned PUT usa credenciales del
  firmante; el Block Public Access del bucket no lo bloquea (CORS es ortogonal a las políticas públicas).
- IAM del Lambda: `Statement` adicional con `s3:PutObject` sobre `arn:.../media/*` (mínimo privilegio).
- Env vars del Lambda: `MEDIA_BUCKET = !Ref FrontendBucket`,
  `MEDIA_PUBLIC_BASE = https://${FrontendDistribution.DomainName}`. Sin ciclos de dependencia
  (Function → Distribution → Bucket).

### 3. Frontend admin: galería de imágenes

`products.html` reemplaza el único campo URL por una **galería**: input file (subida) + input URL
(alternativo), lista de miniaturas con botón quitar y reordenar; la primera miniatura es la principal.
`products.js` mantiene `images: list[str]`, sube por presign y arma el arreglo. La gestión de categorías
se ofrece en un panel/modal: listar, agregar, eliminar (deshabilitando eliminar si está en uso).

## Riesgos y mitigaciones

- **Archivos no-imagen / muy grandes:** se restringe `content_type` a `image/*` en el presign; el tamaño
  se valida en el cliente (límite, p. ej. 5 MB) antes de pedir la URL.
- **Categoría en uso eliminada:** el `DELETE` valida uso y responde 409 con mensaje claro.
- **CORS demasiado abierto:** en dev `AllowedOrigin` puede ser `*`; en prod se fija al dominio CloudFront.

## Alternativas descartadas

- **Bucket de media dedicado + 2ª distribución:** más infra y costo, innecesario en tier-0; el bucket de
  frontend ya está detrás de CloudFront.
- **Subir el binario por el API (multipart al Lambda):** límite de 10 MB de API Gateway, mayor costo y
  acoplamiento; el presigned PUT es el patrón serverless idiomático.
