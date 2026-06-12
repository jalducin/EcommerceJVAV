## ADDED Requirements

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

### Requirement: Despliegue gateado por disponibilidad de la plantilla SAM

Mientras no exista la plantilla SAM (`template.yaml`), la etapa de despliegue SHALL detectar su ausencia y
finalizar sin error indicando que el despliegue está pendiente, para no romper el pipeline en `main`.

#### Scenario: Sin template.yaml, deploy queda pendiente

- **WHEN** se ejecuta la etapa de despliegue y no existe `template.yaml`
- **THEN** registra que el despliegue está pendiente (IaC del Sprint 0)
- **AND** la etapa no falla el pipeline
