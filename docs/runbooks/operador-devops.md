# Runbook — Operador / DevOps

## Objetivo

Operar la plataforma serverless de MetalShop: desplegar el stack con AWS SAM, sembrar datos demo, publicar el frontend en S3 + CloudFront, rotar secretos del vault de conectores, leer logs y la DLQ, y hacer teardown del stack de forma segura.

## Precondiciones

- AWS CLI y AWS SAM CLI instalados y autenticados contra la cuenta `957266312835`.
- **Docker corriendo** (el build de SAM se hace siempre en contenedor — ver gotcha abajo).
- Poetry instalado (para el seed local) y Python 3.11.
- Permisos IAM para CloudFormation, Lambda, API Gateway, DynamoDB, S3, CloudFront, Secrets Manager y CloudWatch Logs.
- Datos del entorno `dev`:

| Recurso | Valor |
|---|---|
| Stack | `metalshop-dev` |
| Región | `us-east-2` |
| Lambda | `metalshop-api-dev` |
| Log group | `/aws/lambda/metalshop-api-dev` |
| Tabla | `metalshop-dev` |
| Bucket frontend | `metalshop-frontend-dev-957266312835` |
| Distribución CloudFront | `E3J6D06L3SRBXS` |
| API base | `https://cizs8fa7lf.execute-api.us-east-2.amazonaws.com/dev` |
| Frontend | `https://d3rw1q49m6mvnq.cloudfront.net` |

> **Gotcha del stage (Mangum):** el handler usa `Mangum(app, api_gateway_base_path=f"/{ENVIRONMENT}")`. El stage del HTTP API (`/dev`) va en el path y Mangum lo recorta para que FastAPI vea `/api/...`. El stage **debe coincidir** con la variable `ENVIRONMENT` (`dev`). Si no coinciden, todas las rutas dan `404`/`{"detail":"Not Found"}`.

## Pasos

### 1. Build (¡siempre con contenedor!)

```bash
sam build --use-container
```

> **Gotcha de `sam build` sin contenedor:** compilar sin `--use-container` produce un paquete sin las dependencias correctas y la Lambda falla en runtime con `No module named fastapi` (u otras libs). **Usa siempre `--use-container`.**

### 2. Deploy

La configuración vive en `samconfig.toml` (`stack_name=metalshop-dev`, `region=us-east-2`, `Environment=dev`, `capabilities=CAPABILITY_IAM`, `confirm_changeset=false`).

```bash
sam deploy
```

> **Subida de imágenes (presigned PUT).** El stack inyecta al Lambda `MEDIA_BUCKET` (el bucket de
> frontend) y `MEDIA_PUBLIC_BASE` (dominio CloudFront), añade permiso de mínimo privilegio
> `s3:PutObject` solo sobre `media/*`, y declara CORS (`PUT/GET/HEAD` desde `FrontendUrl`) en el bucket.
> No hay bucket ni distribución nuevos. Las imágenes subidas quedan bajo `media/` y se sirven por el
> mismo CloudFront.

Salida esperada: actualización/creación del stack `metalshop-dev` con los outputs `ApiUrl`, `FrontendUrl` y `TableName`. En primer deploy, pasar `SecretKey` real:

```bash
sam deploy --parameter-overrides "Environment=dev SecretKey=$(openssl rand -hex 32)"
```

### 3. Sembrar la tabla (datos demo + admin)

El seed es **idempotente**. La tabla ya existe (la crea el stack), así que usa `--no-create-table`:

```bash
DYNAMODB_TABLE=metalshop-dev AWS_REGION=us-east-2 \
  poetry run python seed_dynamodb.py --no-create-table
```

Siembra la config de tienda, los productos demo y el admin `admin@metalshop.mx` / `Admin123!` (si no existe).

### 4. Publicar el frontend en S3 + invalidar CloudFront

```bash
# Subir los estáticos al bucket del frontend
aws s3 sync frontend/ "s3://metalshop-frontend-dev-957266312835/" \
  --delete --region us-east-2

# Invalidar la caché de CloudFront para servir la versión nueva
aws cloudfront create-invalidation \
  --distribution-id E3J6D06L3SRBXS --paths "/*"
```

### 5. Rotar secretos del vault de conectores

Las credenciales viven en AWS Secrets Manager, un secreto por conector: `metalshop/connectors/<conector>` (p. ej. `metalshop/connectors/shopify`). La app las lee con `vault.get_credentials()`; nunca van en código ni en la tabla de datos.

```bash
# Rotar (actualizar el valor del secreto). Idempotente: crea si falta, actualiza si existe.
aws secretsmanager put-secret-value \
  --secret-id "metalshop/connectors/shopify" \
  --secret-string '{"api_key":"NUEVA_KEY","api_secret":"NUEVO_SECRET"}' \
  --region us-east-2

# Confirmar el valor vigente
aws secretsmanager get-secret-value \
  --secret-id "metalshop/connectors/shopify" --region us-east-2 \
  --query SecretString --output text
```

### 6. Leer logs (CloudWatch) y revisar la DLQ

```bash
# Logs en vivo de la Lambda
sam logs --stack-name metalshop-dev --name Api --tail

# Equivalente con AWS CLI (últimos 30 min)
aws logs tail "/aws/lambda/metalshop-api-dev" --since 30m --follow --region us-east-2
```

Para la **DLQ** (mensajes muertos de sincronización/ingesta de conectores): inspeccionar **sin reprocesar a ciegas**.

```bash
# Localizar la cola DLQ del stack
aws sqs list-queues --region us-east-2 --queue-name-prefix metalshop

# Atributos: cuántos mensajes acumulados
aws sqs get-queue-attributes --region us-east-2 \
  --queue-url "<DLQ_URL>" \
  --attribute-names ApproximateNumberOfMessages

# Inspeccionar un mensaje SIN borrarlo (visibility temporal corta)
aws sqs receive-message --region us-east-2 \
  --queue-url "<DLQ_URL>" --max-number-of-messages 1 --visibility-timeout 5
```

Reprocesa solo **después** de corregir la causa raíz; el reproceso debe ser idempotente para no duplicar efectos.

### 7. Teardown del stack

```bash
sam delete --stack-name metalshop-dev --region us-east-2
```

Elimina la Lambda, API Gateway, DynamoDB, S3, CloudFront, etc. del stack. **Operación destructiva:** ver advertencia en Troubleshooting.

## Verificación

- Tras `sam deploy`, los outputs muestran `ApiUrl`/`FrontendUrl`/`TableName` correctos y el stack queda en `UPDATE_COMPLETE`/`CREATE_COMPLETE`.
- Health: `curl -s "https://cizs8fa7lf.execute-api.us-east-2.amazonaws.com/dev/api/health"` devuelve `{"status":"ok","env":"dev"}`.
- Tras el seed: `curl -s ".../dev/api/products"` devuelve `total > 0`.
- Tras publicar el frontend e invalidar: el storefront `https://d3rw1q49m6mvnq.cloudfront.net` sirve la versión nueva (forzar recarga sin caché).
- Tras rotar un secreto: el conector **sigue autenticando** (su estado en `GET /api/admin/connectors` no degrada).
- DLQ inspeccionada: `ApproximateNumberOfMessages` conocido y los mensajes revisados sin haberse borrado.

## Troubleshooting

| Síntoma | Causa probable | Acción correctiva |
|---|---|---|
| Lambda falla con `No module named fastapi` | `sam build` ejecutado **sin** contenedor | Reconstruir con `sam build --use-container` y volver a `sam deploy`. |
| Todas las rutas dan `404` / `Not Found` | Stage del HTTP API ≠ `ENVIRONMENT` (gotcha de Mangum `api_gateway_base_path`) | Asegurar `Environment=dev` y stage `/dev`; redeploy. Probar `.../dev/api/health`. |
| `sam deploy` falla por permisos | Rol IAM sin permisos sobre algún recurso | Revisar el error de CloudFormation; otorgar permisos faltantes (Lambda/DynamoDB/S3/CloudFront/Secrets/Logs). |
| Stack en `ROLLBACK_COMPLETE` / `UPDATE_ROLLBACK_FAILED` | Error durante el cambio (recurso inválido, límite, dependencia) | Leer eventos: `aws cloudformation describe-stack-events --stack-name metalshop-dev`; corregir y redeploy; si quedó inservible, `sam delete` y recrear. |
| Frontend viejo tras publicar | Caché de CloudFront no invalidada | Crear invalidación `--paths "/*"` en `E3J6D06L3SRBXS`; esperar a que termine. |
| Conector deja de autenticar tras rotar | Secreto rotado con valor inválido o formato JSON incorrecto | Verificar con `get-secret-value`; volver a poner el JSON correcto con `put-secret-value`; confirmar estado del conector en el panel admin. |
| DLQ acumulando mensajes | Fallo persistente en sync/ingesta de un conector | Inspeccionar un mensaje (sin borrar), diagnosticar la causa en los logs estructurados; **solo entonces** reprocesar de forma idempotente. |
| Teardown deja datos huérfanos o falla | Bucket S3 no vacío / recursos retenidos | Vaciar el bucket antes (`aws s3 rm s3://metalshop-frontend-dev-957266312835/ --recursive`) y reintentar `sam delete`. **Destructivo:** elimina la tabla `metalshop-dev` y todos sus datos; haz respaldo si aplica. |
