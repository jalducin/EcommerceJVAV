## Context

Ajustes post-apply aplicados como hotfixes sobre el stack en vivo; se documentan bajo SDD.

## Goals / Non-Goals

**Goals:** marca configurable en UI, acceso al panel correcto, Swagger bajo stage, catálogo demo realista.
**Non-Goals:** cambios de arquitectura; sigue siendo Lambdalith + DynamoDB + S3/CloudFront.

## Decisions

### Decisión 1: root_path al stage
FastAPI `root_path=/<ENVIRONMENT>` (dev/prod en Lambda; vacío en local) para que Swagger pida el
openapi con el prefijo del stage. Mangum sigue recortando el stage para el ruteo.

### Decisión 2: marca data-driven
El nombre se inyecta desde `/api/config` en `data-store-name`; no se hardcodea el vertical.

### Decisión 3: guard no-admin -> login
Mejor UX para cambiar de cuenta que rebotar a inicio.

## Risks / Trade-offs

- Local con `ENVIRONMENT=development` no usa stage -> root_path vacío (correcto).
