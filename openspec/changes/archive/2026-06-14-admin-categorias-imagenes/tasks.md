# Tasks: Gestión de categorías e imágenes de producto en el panel admin

## Step 0 — Crear feature branch (SIEMPRE PRIMERO)
- [x] Crear y cambiar a `feature/admin-categorias-imagenes`

## 1. Backend — Categorías (admin)
- [x] 1.1 Schemas `CategoryCreate` / `CategoryList` en `backend/schemas/admin_media.py`
- [x] 1.2 `GET /api/admin/categories` (lista desde config)
- [x] 1.3 `POST /api/admin/categories` idempotente, sin duplicados (trim, case-insensitive) → 201
- [x] 1.4 `DELETE /api/admin/categories/{name}` → 204; 409 si está en uso por producto activo
- [x] 1.5 Persistir vía `store_repo.put_config()` (`backend/category_service.py`)

## 2. Backend — Subida de imágenes (presign)
- [x] 2.1 Servicio de uploads: `generate_presigned_url` (PUT, `media/<uuid>.<ext>`, expira 300s)
- [x] 2.2 `POST /api/admin/uploads/presign` → `{ upload_url, public_url, key }`; solo `image/*` (422 si no)
- [x] 2.3 Env vars `MEDIA_BUCKET`, `MEDIA_PUBLIC_BASE` en `config.py`
- [x] 2.4 Endpoints en router `admin` (ya registrado) + tags/summary OpenAPI

## 3. Infra (template.yaml) — OPERADOR/DevOps
- [x] 3.1 `FrontendBucket.CorsConfiguration` (PUT/GET/HEAD desde `FrontendUrl`, ExposedHeaders ETag)
- [x] 3.2 IAM Lambda: `s3:PutObject` sobre `arn:.../media/*` (mínimo privilegio)
- [x] 3.3 Env vars del Lambda: `MEDIA_BUCKET`, `MEDIA_PUBLIC_BASE` (CloudFront domain)

## 4. Frontend admin
- [x] 4.1 `products.html`: galería de imágenes (subida + URL, miniaturas, quitar/reordenar)
- [x] 4.2 `products.js`: subir por presign, armar `images: list[str]`, principal = primera
- [x] 4.3 Modal de categorías: listar, agregar, eliminar (deshabilitar si en uso)

## Step N — Revisar y actualizar pruebas existentes (OBLIGATORIO)
- [x] Revisar tests de catálogo/admin afectados (sin regresiones; suite 91 passed)

## Step N+1 — Ejecutar pruebas y verificar estado (OBLIGATORIO) — EL AGENTE EJECUTA
- [x] Ejecutar pruebas dirigidas (8) y suite completa (91); sin regresiones
- [x] Reporte en `reports/2026-06-14-step-N+1-pruebas-y-verificacion.md`

## Step N+2 — Verificación manual (API/HTTP) (OBLIGATORIO) — EL AGENTE EJECUTA
- [x] Probado: categorías add/list/dup/delete(204)/delete-en-uso(409), presign válido/inválido/sin-auth
- [x] Estado restaurado (moto efímero; sin tocar AWS real)

## Step N+3 — Actualizar documentación técnica (OBLIGATORIO)
- [x] Runbook operador (env MEDIA_*, CORS, IAM) actualizado; specs OpenSpec como fuente canónica

## Step N+4 — Runbook del administrador (OBLIGATORIO)
- [x] `docs/runbooks/administrador.md`: secciones 6 (categorías) y 7 (imágenes) + verificación/troubleshooting

## Step N+5 — Pruebas unitarias de la lógica nueva (OBLIGATORIO)
- [x] `tests_serverless/test_admin_categories_uploads.py` (8 pruebas): categorías y presign

## Step N+6 — Swagger/OpenAPI al día (OBLIGATORIO)
- [x] `summary`, `description`, `tags`, `response_model` y errores (409/422/503) en endpoints nuevos
