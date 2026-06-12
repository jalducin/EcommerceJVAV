## 0. Preparación (OBLIGATORIO)

- [ ] 0.1 Crear y cambiar a la feature branch `feature/ci-cd-pipeline` (Step 0 — SIEMPRE primero)
- [ ] 0.2 Leer `openspec/config.yaml`, `docs/aws-serverless-standards.md` y la regla de pasos obligatorios

## 1. Job CI (repo de código)

- [ ] 1.1 Crear `.github/workflows/ci-cd.yml` con job `ci` (push + pull_request)
- [ ] 1.2 Pasos: checkout, Python 3.11, instalar Poetry + deps (con cache)
- [ ] 1.3 Lint con Ruff y `pytest tests_serverless/` (DynamoDB mockeado con moto)
- [ ] 1.4 Variables de entorno de prueba (SECRET_KEY dummy, región); sin secretos reales

## 2. Job CD (AWS) gateado

- [ ] 2.1 Job `deploy` con `needs: [ci]` y `if: ref == main && event == push`
- [ ] 2.2 Autenticación AWS por OIDC (o Secrets) con `aws-actions/configure-aws-credentials`
- [ ] 2.3 Instalar SAM; paso guard `test -f template.yaml` (si no existe, "pendiente" sin fallar)
- [ ] 2.4 `sam build` + `sam deploy --no-confirm-changeset --no-fail-on-empty-changeset` por entorno

## 3. Retiro del workflow legacy

- [ ] 3.1 Reemplazar/eliminar `.github/workflows/ci.yml` (validaba el monolito)

## 4. Verificación (OBLIGATORIO — EL AGENTE EJECUTA)

- [ ] 4.1 Validar la sintaxis del workflow (acción de lint de YAML / `act` o revisión)
- [ ] 4.2 Confirmar que `pytest tests_serverless/` y `ruff` pasan localmente igual que en CI
- [ ] 4.3 Verificar en GitHub que CI corre en un PR y que `deploy` NO corre en ramas feature/PR
- [ ] 4.4 Reporte en `specs/ci-cd-pipeline/reports/AAAA-MM-DD-step-4-verificacion.md`

## 5. Configuración de secretos (OBLIGATORIO antes de habilitar deploy real)

- [ ] 5.1 Configurar rol OIDC de despliegue (mínimo privilegio) o secrets AWS en GitHub
- [ ] 5.2 Definir variables de región/entorno

## 6. Documentación (OBLIGATORIO)

- [ ] 6.1 Documentar el flujo CI/CD y los secrets requeridos en `README.md`
- [ ] 6.2 Actualizar `docs/roadmap-plataforma-multicanal.md` / `docs/aws-serverless-standards.md`
- [ ] 6.3 Verificar consistencia documental: 0 referencias rotas
