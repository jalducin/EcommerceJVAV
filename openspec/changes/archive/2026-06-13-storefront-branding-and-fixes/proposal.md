## Why

Tras la migración serverless y el panel admin, varios ajustes de UI/branding se aplicaron
como hotfixes directos sobre el stack en vivo (rebrand a "JV Market", arreglo de acceso al
panel, Swagger bajo el stage, catálogo demo con imágenes reales). Este cambio los registra
bajo SDD para que la documentación refleje el estado real (base-standards §7).

## What Changes

- **Marca configurable en UI:** el nombre de tienda se renderiza desde `/api/config`
  (`data-store-name`); se retiró el copy fijo de un vertical ("herramientas/acero"). Marca por
  defecto: **JV Market**.
- **Acceso al panel:** una sesión no-admin (p. ej. cliente) que entra a `/admin/*` ahora se
  redirige a `login` con `next` (para entrar como admin), en vez de rebotar a inicio.
- **Swagger bajo el stage:** la documentación OpenAPI se sirve correctamente bajo el prefijo
  del stage de API Gateway (`root_path`), evitando el 404 de `openapi.json`.
- **Catálogo demo:** dataset por defecto ampliado a 12 productos en 3 categorías con imágenes
  reales servidas desde S3/CloudFront, más una cuenta cliente demo.

## Capabilities

### Modified Capabilities
- `store-configuration`: la marca se consume desde la configuración en el frontend.
- `admin-auth-ui`: comportamiento de redirección para sesiones no-admin.
- `api-swagger`: la doc OpenAPI respeta el prefijo del stage.

## Impact

- Frontend: `index.html` (hero/footer), `js/api.js`, `js/config.js`, `js/pages/catalog.js`,
  `js/admin/guard.js`, `admin/dashboard.html` (faltaba `variables.css`).
- Backend: `backend/app.py` (`root_path` al stage, título OpenAPI).
- Datos: `seed_dynamodb.py` (12 productos, imágenes `/img/products`, cliente demo).
- Verificado en vivo (CloudFront + API Gateway).
