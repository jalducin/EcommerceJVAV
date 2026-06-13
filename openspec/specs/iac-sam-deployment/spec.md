# iac-sam-deployment Specification

## Purpose
TBD - created by archiving change migrate-to-serverless-aws. Update Purpose after archive.
## Requirements
### Requirement: Stack desplegable con AWS SAM

El stack completo SHALL definirse como infraestructura como código en una plantilla AWS SAM
(`template.yaml`), incluyendo Lambda, API Gateway, tabla DynamoDB + GSIs, bucket S3, distribución
CloudFront, identidad SES y roles IAM. El despliegue SHALL ser reproducible con `sam build` y `sam deploy`.

#### Scenario: Despliegue desde cero

- **WHEN** se ejecuta `sam build` seguido de `sam deploy` en una cuenta limpia
- **THEN** se crean todos los recursos del stack
- **AND** las salidas (outputs) incluyen la URL de la API y la del frontend (CloudFront)

#### Scenario: Recursos parametrizados por entorno

- **WHEN** se despliega indicando un entorno (p. ej. `dev`)
- **THEN** los nombres de recursos y variables se parametrizan por ese entorno
- **AND** un segundo entorno puede coexistir sin colisiones

### Requirement: Permisos IAM de mínimo privilegio

El rol de ejecución de la Lambda SHALL conceder solo los permisos necesarios: operaciones sobre la tabla
DynamoDB y sus GSIs, y envío vía SES. NO SHALL otorgar permisos amplios (p. ej. `*` sobre todos los
recursos).

#### Scenario: Lambda accede solo a sus recursos

- **WHEN** la Lambda intenta operar sobre su tabla DynamoDB y enviar por SES
- **THEN** las operaciones permitidas tienen éxito
- **AND** el rol no incluye permisos sobre recursos ajenos al stack

### Requirement: Ejecución local equivalente

El proyecto SHALL permitir ejecutar y verificar el stack localmente con DynamoDB Local y SAM local
(`sam local start-api`), de modo que el flujo se pueda validar sin desplegar en la nube.

#### Scenario: API local contra DynamoDB Local

- **WHEN** se levanta `sam local start-api` con DynamoDB Local y datos sembrados
- **THEN** los endpoints responden igual que en el despliegue en la nube
- **AND** el flujo de compra puede ejecutarse de extremo a extremo en local

