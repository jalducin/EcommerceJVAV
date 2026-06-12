## Why

El proyecto necesita integración y entrega continuas en GitHub Actions con una regla clara de
secuenciación: **primero se valida el repositorio de código (lint + pruebas) y solo si pasa se despliega
a AWS**. Esto evita desplegar código roto y hace reproducible el camino a producción serverless.

## What Changes

- Se añade un pipeline de **GitHub Actions** con dos etapas secuenciales:
  1. **CI (repo de código)**: en cada push y pull request, instala dependencias, corre Ruff (lint) y la
     suite de pruebas (DynamoDB mockeado con moto). Es la compuerta de calidad.
  2. **CD (AWS)**: solo en `main` y **solo si la etapa CI pasó** (`needs: ci`), construye y despliega el
     stack serverless a AWS con SAM.
- Las credenciales de AWS se inyectan desde **GitHub Secrets/OIDC**, nunca en el repo.
- El despliegue se activa cuando exista la plantilla SAM (`template.yaml`, del cambio
  `migrate-to-serverless-aws`); mientras tanto el job CD queda gateado y documentado.
- Se reemplaza el workflow legacy (`ci.yml`) que validaba el monolito.

## Capabilities

### New Capabilities
- `ci-cd-pipeline`: pipeline de GitHub Actions que valida el código (lint+pruebas) y, solo si pasa,
  despliega el stack serverless a AWS; con la regla de secuenciación repo → AWS.

### Modified Capabilities
<!-- Relacionada con iac-sam-deployment (migrate-to-serverless-aws), que provee template.yaml. -->

## Impact

- **CI/CD**: nuevo `.github/workflows/ci-cd.yml` (jobs `ci` y `deploy`); se retira/integra `ci.yml`.
- **Secrets**: requiere configurar en GitHub el rol/credenciales de AWS (OIDC recomendado) y la región.
- **Dependencia**: el deploy efectivo requiere `template.yaml` (SAM) del cambio `migrate-to-serverless-aws`.
- **Docs**: actualizar README/roadmap con el flujo de CI/CD y los secrets requeridos.
