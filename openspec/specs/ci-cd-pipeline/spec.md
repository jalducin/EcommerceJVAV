# ci-cd-pipeline Specification

## Purpose
TBD - created by archiving change ci-cd-pipeline. Update Purpose after archive.
## Requirements
### Requirement: CI valida el repositorio de código

El pipeline SHALL ejecutar una etapa de Integración Continua en cada push y pull request que instale
dependencias, ejecute el linter (Ruff) y la suite de pruebas. Si el lint o las pruebas fallan, la etapa
CI SHALL fallar y bloquear cualquier despliegue.

#### Scenario: Pull request con pruebas en verde

- **WHEN** se abre un pull request y el lint y las pruebas pasan
- **THEN** la etapa CI termina en éxito
- **AND** habilita la posibilidad de desplegar (en main)

#### Scenario: Pruebas en rojo bloquean el pipeline

- **WHEN** las pruebas o el lint fallan
- **THEN** la etapa CI falla
- **AND** la etapa de despliegue NO se ejecuta

### Requirement: CD despliega a AWS solo tras CI y solo en main

La etapa de Entrega Continua (despliegue a AWS) SHALL depender de la etapa CI (`needs: ci`) y SHALL
ejecutarse únicamente en la rama `main`. NO SHALL desplegarse desde ramas de feature ni pull requests, ni
si CI no pasó. Esta es la regla **primero repo de código, después AWS**.

#### Scenario: Merge a main con CI verde despliega

- **WHEN** se hace push/merge a `main` y la etapa CI pasa
- **THEN** la etapa de despliegue construye y publica el stack serverless en AWS (SAM)

#### Scenario: Push a rama de feature no despliega

- **WHEN** se hace push a una rama `feature/*`
- **THEN** corre CI pero la etapa de despliegue no se ejecuta

#### Scenario: CI fallida no despliega aunque sea main

- **WHEN** un push a `main` tiene CI en rojo
- **THEN** la etapa de despliegue no se ejecuta

### Requirement: Credenciales de AWS seguras (sin secretos en el repo)

El despliegue SHALL autenticarse con AWS mediante GitHub Secrets u OIDC (rol federado), nunca con
credenciales en el repositorio. La región y el entorno SHALL ser parametrizables.

#### Scenario: Deploy autenticado por secretos/OIDC

- **WHEN** la etapa de despliegue se ejecuta
- **THEN** obtiene las credenciales de AWS desde Secrets/OIDC configurados en GitHub
- **AND** no existe ningún secreto de AWS versionado en el repositorio

### Requirement: Despliegue con opt-in explícito (no romper main)

La etapa de despliegue SHALL requerir un opt-in explícito (variable de repositorio
`AWS_DEPLOY_ENABLED=true`) además de `main`, push y CI verde. Mientras el opt-in no esté activo (p. ej.
antes de configurar el rol OIDC), la etapa de despliegue NO SHALL ejecutarse, de modo que `main` no se
rompa. Como salvaguarda adicional, si no existe `template.yaml`, el job SHALL terminar sin error
indicando que el despliegue está pendiente.

#### Scenario: Sin opt-in, no se intenta desplegar

- **WHEN** se hace push a `main` con CI verde pero sin `AWS_DEPLOY_ENABLED=true`
- **THEN** la etapa de despliegue no se ejecuta
- **AND** el pipeline en `main` permanece verde

#### Scenario: Con opt-in pero sin template.yaml

- **WHEN** el opt-in está activo pero no existe `template.yaml`
- **THEN** el job registra que el despliegue está pendiente (IaC)
- **AND** la etapa no falla el pipeline

