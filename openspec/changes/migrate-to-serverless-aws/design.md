## Context

MetalShop es un monolito FastAPI async (SQLAlchemy 2.0 + SQLite/PostgreSQL, Alembic) con frontend
estático servido por `StaticFiles`, JWT, `slowapi` y `fastapi-mail`. Se quiere llevar a **serverless en
AWS free tier permanente** para aprendizaje y, de paso, convertirlo en una **plataforma ecommerce
configurable** (business-agnostic) con una demo de ropa/tenis funcional de extremo a extremo.

Restricciones: costo ~0 (tier 0), sin frameworks JS/CSS en frontend, documentación en español. La capa de
servicios (`backend/services/*`) ya concentra la lógica de negocio, pero está acoplada a sesiones
SQLAlchemy: ahí se concentra la reescritura.

## Goals / Non-Goals

**Goals:**
- Ejecutar la API como Lambda (Mangum) detrás de API Gateway, sin estado.
- Persistir todo en una tabla DynamoDB single-table que cubra los patrones de acceso actuales.
- Modelo de producto genérico (variantes con atributos arbitrarios), no atado a un vertical.
- Configuración de tienda (marca, categorías, moneda, impuestos/envío, tema) que haga la tienda adaptable.
- Frontend en S3/CloudFront, email por SES, throttling por API Gateway, todo definido con AWS SAM.
- Dataset demo intercambiable (ropa/tenis por defecto) y flujo de compra/admin verificado E2E.

**Non-Goals:**
- Pagos reales (sigue en modo simulado, como v1).
- Multi-tenant real (varias tiendas aisladas simultáneas): la config es por despliegue, no por inquilino.
- Búsqueda full-text avanzada (la búsqueda por nombre se resuelve simple; ver Decisiones).
- Microservicios / una Lambda por endpoint: se usa Lambdalith.

## Decisions

### Decisión 1: Compute — Lambdalith con Mangum sobre API Gateway HTTP API

Toda la app FastAPI en una sola Lambda adaptada con Mangum. Alternativas: una Lambda por endpoint (más
"serverless puro" pero mucha fricción y peor DX para aprender) o Fargate (no escala a cero, no tier 0).
El Lambdalith es el mejor equilibrio simplicidad/costo para aprendizaje. `bcrypt` (passlib, cost 12) es
CPU-intensivo: se sube la memoria de la Lambda (más vCPU) o se baja el cost factor en `dev`.

### Decisión 2: Datos — DynamoDB single-table

Una tabla con PK/SK + GSIs. Alternativa RDS descartada por costo (12 meses + RDS Proxy) y por
connection management en Lambda. Esquema propuesto (claves lógicas):

```
Tabla: MetalShop  (PK, SK)  + GSIs

Entidad     PK                 SK                       GSIs / notas
--------    -----------------  -----------------------  -----------------------------------------
User        USER#<id>          PROFILE                  GSI1: GSI1PK=EMAIL#<email>, GSI1SK=USER  (login por email)
Product     PRODUCT#<id>       PRODUCT                  GSI2: GSI2PK=CAT#<categoria>, GSI2SK=PRODUCT#<id> (listar por categoría)
  variantes embebidas en el item del producto: lista de {attrs:{...}, stock, price_delta, sku}
CartItem    USER#<id>          CART#<product_id>#<vkey> query begins_with(SK, "CART#")  (carrito por usuario)
Order       USER#<id>          ORDER#<created_at>#<id>  items embebidos (denormalizados) en el item del pedido
  índice admin: GSI3PK=ORDERS, GSI3SK=<status>#<created_at>  (todos los pedidos + filtro por estado)
  ventas del día: GSI3 permite filtrar por created_at; o atributo DATE#<yyyy-mm-dd>
StoreConfig CONFIG             STORE                    documento único de configuración de tienda
```

- **Variantes genéricas**: se embeben en el item del producto como lista de objetos con `attrs` (mapa
  arbitrario), `stock`, `price_delta`, `sku`. Cumple el requisito business-agnostic sin tablas por vertical.
- **Pedido denormalizado**: los `OrderItem` se guardan como lista dentro del pedido (no hay JOINs en
  DynamoDB). Se copia `unit_price` y atributos de variante al momento de la compra.
- **Búsqueda por nombre**: con catálogo ≤ 1000 (restricción de SPEC v1), se resuelve con `Query` por
  categoría + filtro, o `Scan` acotado con filtro `contains`. Se documenta el límite; full-text se deja
  fuera de alcance.
- **Stock bajo / métricas admin**: `Scan` con filtro acotado (catálogo pequeño) o GSI sparse `LOWSTOCK`.
  Para aprendizaje se acepta `Scan` acotado y se documenta el trade-off.

### Decisión 3: Checkout atómico con TransactWriteItems

El checkout usa `TransactWriteItems`: `Put` del pedido + `Update` condicional del stock de cada variante
(`ConditionExpression` stock ≥ qty). Si cualquier condición falla, la transacción completa se revierte.
Sustituye a la transacción SQL actual.

### Decisión 4: Configuración de tienda como documento + endpoint

`StoreConfig` vive como item único en DynamoDB (`CONFIG/STORE`) y se expone por `GET /api/config`. El
frontend se renderiza data-driven (marca, categorías, moneda, tema vía CSS Custom Properties). Cambiar de
negocio = reemplazar este documento (+ dataset). Alternativa (variables de entorno) descartada por ser
menos flexible para categorías/tema y requerir redeploy.

### Decisión 5: Frontend en S3 + CloudFront; API por API Gateway

Se elimina `StaticFiles` de producción. `frontend/js/api.js` toma la base URL de la API por configuración
(inyectada en build/deploy). CORS configurado en el backend para el dominio de CloudFront.

### Decisión 6: Email por SES; throttling por API Gateway

`fastapi-mail`/SMTP → SES (SDK boto3 o SMTP de SES). `slowapi` (estado en memoria, inútil en Lambda) →
throttling por ruta en API Gateway. Ambos definidos en SAM.

### Decisión 7: IaC con AWS SAM + ejecución local

`template.yaml` (SAM) define Lambda, HTTP API, tabla+GSIs, S3, CloudFront, SES y roles IAM de mínimo
privilegio. Verificación local con DynamoDB Local + `sam local start-api`. Alternativas: Serverless
Framework o CDK; SAM se elige por ser nativo de AWS y didáctico para empezar.

### Decisión 8: Tests con DynamoDB Local / moto

`tests/conftest.py` pasa de SQLite in-memory a DynamoDB Local (o `moto`) creando la tabla+GSIs por test.
Se añaden pruebas de variantes, configuración de tienda, cargador idempotente y checkout transaccional.

## Risks / Trade-offs

- **Reescritura de la capa de datos** → Mitigación: aislar acceso a datos en un repositorio/cliente
  DynamoDB detrás de los `services/`; migrar capability por capability con sus tests.
- **Pérdida de JOINs y queries ad-hoc** → Mitigación: modelar por patrones de acceso (arriba) y
  denormalizar pedidos; documentar lo que queda como `Scan` acotado.
- **Cold starts y bcrypt CPU-pesado** → Mitigación: subir memoria de la Lambda; cost factor menor en dev.
- **Búsqueda/stock-bajo vía Scan** → Mitigación: aceptable para ≤1000 productos; documentar y dejar GSI
  sparse como evolución futura.
- **SES en sandbox** (solo destinatarios verificados) → Mitigación: documentar verificación de identidades
  y solicitud de salida de sandbox; el fallo de email no revierte el pedido.
- **Alcance grande en un solo cambio** → Mitigación: las 10 capabilities están desacopladas; el `tasks.md`
  permite implementarlas y verificarlas de forma incremental. Si se prefiere, puede dividirse en varios
  cambios OpenSpec (infra primero, luego plataforma configurable, luego UX).

## Migration Plan

1. Aislar acceso a datos detrás de un cliente DynamoDB; crear tabla+GSIs en SAM y DynamoDB Local.
2. Migrar entidades y servicios a DynamoDB (User → Product/variantes → Cart → Order/checkout txn).
3. Introducir `StoreConfig` + `GET /api/config` y hacer el cálculo de totales data-driven.
4. Adaptar `main.py` (Mangum, sin StaticFiles), email (SES), throttling (API Gateway), quitar slowapi/alembic.
5. Cargador `seed_dynamodb.py` idempotente con dataset ropa/tenis por defecto.
6. Mejoras de frontend data-driven (categorías, selector de variante, galería, estados); base URL por config.
7. SAM completo (S3+CloudFront, SES, IAM) y verificación local; luego deploy.
8. Verificación E2E (cliente + admin) con reporte; actualizar docs.

**Rollback**: el código v1 (SQLAlchemy/Docker) permanece en `main` hasta validar; la rama del cambio se
mantiene aislada. Si el camino DynamoDB se complica, RDS Postgres queda como fallback documentado.

## Open Questions

- ¿Function URL de Lambda en vez de API Gateway para simplificar aún más? (Throttling y rutas favorecen
  API Gateway HTTP API; se mantiene salvo que se priorice máxima simplicidad.)
- ¿Imágenes del catálogo en S3 propio o URLs externas para la demo? (Para demo, URLs externas; subida real
  a S3 queda como evolución, ya estaba en backlog v2.)
- ¿Región AWS objetivo y presupuesto/alarma de billing para proteger el tier 0?
