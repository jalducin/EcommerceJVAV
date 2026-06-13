## Context

App serverless (Lambdalith) con docs públicos. Se quiere cerrar el acceso conservando la utilidad.

## Goals / Non-Goals

**Goals:** docs no públicos; usables por el equipo con credenciales; off por defecto si no hay password.
**Non-Goals:** SSO/OAuth para docs; cambiar la auth de la API (sigue JWT).

## Decisions

### Decisión 1: Basic auth en rutas propias de docs
Se desactivan los docs nativos (docs_url/redoc_url/openapi_url = None) y se montan rutas propias
`/api/docs`, `/api/redoc`, `/api/openapi.json` con dependencia de HTTP Basic (comparación en tiempo
constante). Respetan el `root_path` del stage.

### Decisión 2: Off por defecto
Si `DOCS_PASSWORD` está vacío, no se registran las rutas de docs (404). Seguro por defecto.

### Decisión 3: Credenciales por entorno
`DOCS_USER`/`DOCS_PASSWORD` desde settings; en AWS via parámetro SAM (NoEcho).

## Risks / Trade-offs

- Basic auth: el navegador reenvía las credenciales al fetch de `openapi.json` (mismo prefijo). Aceptable.
