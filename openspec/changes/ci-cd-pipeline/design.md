## Context

GitHub Actions con dos jobs secuenciales. La regla "primero repo, después AWS" se modela con
dependencia de jobs (`needs`) y condición de rama. Existe un `ci.yml` legacy que validaba el monolito
(hoy en rojo por las dependencias modernas y el código a decomisionar); se reemplaza.

## Goals / Non-Goals

**Goals:**
- Job `ci`: lint (Ruff) + pruebas (moto) en push y PR. Compuerta de calidad.
- Job `deploy`: `needs: ci`, solo en `main`, SAM build + deploy a AWS.
- Credenciales por OIDC/Secrets; deploy gateado por existencia de `template.yaml`.

**Non-Goals:**
- Entornos múltiples (staging/prod) con aprobaciones manuales (evolución futura).
- Pruebas E2E contra AWS real en el pipeline (se hará al madurar el deploy).

## Decisions

### Decisión 1: Secuenciación por `needs`
`deploy` declara `needs: [ci]` y `if: github.ref == 'refs/heads/main' && github.event_name == 'push'`.
Garantiza repo→AWS: sin CI verde no hay deploy; PRs y ramas feature solo corren CI.

### Decisión 2: Alcance de CI durante la migración
La suite verificada vive en `tests_serverless/` (DynamoDB con moto). El job CI corre el lint de los
paquetes serverless y `pytest tests_serverless/`. Cuando se decomisione el monolito (Sprint 0, grupo 11),
CI pasará a `ruff check .` y la suite completa.

### Decisión 3: Autenticación AWS por OIDC (recomendado) o Secrets
Preferir `aws-actions/configure-aws-credentials` con rol OIDC (sin llaves de larga vida). Alternativa:
`AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` en Secrets. Región vía variable/secret.

### Decisión 4: Deploy gateado por `template.yaml`
Un paso comprueba `test -f template.yaml`; si no existe, registra "pendiente" y termina sin fallar. Así el
pipeline en `main` no se rompe antes de que exista la IaC del Sprint 0.

## Risks / Trade-offs

- **Llaves de larga vida** → preferir OIDC; documentar rotación si se usan Secrets.
- **CI parcial durante la migración** → documentado; se amplía a `.` tras el decomiso del monolito.
- **Deploy sin template** → gateado para no romper main.

## Migration Plan

1. Reemplazar `ci.yml` por `ci-cd.yml` con jobs `ci` y `deploy`.
2. Configurar en GitHub el rol OIDC / secrets de AWS y la región.
3. Al existir `template.yaml`, el job `deploy` despliega automáticamente en `main`.

## Open Questions

- ¿OIDC con rol dedicado de despliegue (mínimo privilegio) — ARN del rol?
- ¿Cache de Poetry/SAM para acelerar el pipeline?
