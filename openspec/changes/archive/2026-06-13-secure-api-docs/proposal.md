## Why

La documentación OpenAPI (`/api/docs`, `/api/redoc`, `/api/openapi.json`) está pública en el
stack en vivo: cualquiera que adivine la URL ve el contrato completo de la API. Hay que ponerle
candado sin perder la utilidad para el equipo.

## What Changes

- Los docs (Swagger UI, ReDoc y `openapi.json`) SHALL quedar **protegidos por HTTP Basic auth**
  (usuario/contraseña desde entorno), no públicos.
- Si no hay contraseña configurada (`DOCS_PASSWORD` vacío), los docs SHALL quedar **deshabilitados**
  por completo (404) — seguro por defecto.
- Las credenciales se inyectan por variable de entorno (SAM), nunca en el repo.

## Capabilities

### Modified Capabilities
- `api-swagger`: la doc OpenAPI deja de ser pública; queda tras auth o deshabilitada.

## Impact

- `backend/config.py` (DOCS_USER/DOCS_PASSWORD), `backend/app.py` (rutas de docs con Basic auth),
  `template.yaml` (parámetro DocsPassword + env), CI/CD (sin cambios funcionales).
