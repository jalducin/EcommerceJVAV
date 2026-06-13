# Runbooks operativos — MetalShop (Sprint 8)

Fuente canónica de los procedimientos operativos de MetalShop, organizados **por tipo de usuario**. Cada runbook sigue siempre la misma estructura: **Objetivo · Precondiciones · Pasos · Verificación · Troubleshooting**.

Si un cambio futuro afecta a un tipo de usuario, su runbook se actualiza en el mismo PR (regla SDD §9).

## Tipos de usuario

| Runbook | Para quién | Qué cubre |
|---|---|---|
| [visitante.md](visitante.md) | Cualquiera, sin sesión | Navegar el catálogo, filtrar por categoría, buscar y ver detalle/variantes en el storefront. Solo lectura, sin autenticación. |
| [cliente.md](cliente.md) | Usuario registrado | Registro/login, gestión del carrito, checkout y consulta de pedidos. Incluye ejemplos `curl` contra la API en vivo. |
| [administrador.md](administrador.md) | Usuario con rol `admin` | Panel `/admin/*`, CRUD de productos con variantes, dashboard, pedidos unificados y conectores. |
| [operador-devops.md](operador-devops.md) | Operación / DevOps | Despliegue con SAM, seed de datos, publicación del frontend, rotación de secretos, logs/DLQ y teardown del stack. |

## Entorno de referencia (`dev`)

| Recurso | Valor |
|---|---|
| API (base) | `https://cizs8fa7lf.execute-api.us-east-2.amazonaws.com/dev` |
| Frontend (storefront) | `https://d3rw1q49m6mvnq.cloudfront.net` |
| Stack CloudFormation | `metalshop-dev` |
| Región | `us-east-2` |
| Tabla DynamoDB | `metalshop-dev` |
| Bucket S3 (frontend) | `metalshop-frontend-dev-957266312835` |
| Distribución CloudFront | `E3J6D06L3SRBXS` |
| Admin sembrado | `admin@metalshop.mx` / `Admin123!` |

> Todas las rutas de la API cuelgan del prefijo `/api` y del stage `/dev` (p. ej. `…/dev/api/products`). La API solo expone `/api/*`; el frontend estático se sirve desde S3/CloudFront.

## Documentación relacionada

- OpenAPI / Swagger UI: `…/dev/docs` y esquema en `…/dev/openapi.json` (en `dev`).
- Contratos de conectores no-HTTP: `docs/integrations-standards.md`.
