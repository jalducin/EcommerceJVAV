## Why

MetalShop hoy es un monolito FastAPI con servidor permanente y SQLite/PostgreSQL, con un catálogo de
productos genéricos de prueba. El objetivo de este cambio es triple:

1. **Migrar a una arquitectura serverless en AWS dentro del free tier permanente (tier 0)** con fines de
   aprendizaje: pagar ~0 sin tráfico y aprender el stack serverless nativo (Lambda, API Gateway,
   DynamoDB, S3/CloudFront, SES, IaC con SAM).
2. **Convertirlo en una plataforma ecommerce adaptable a cualquier tipo de negocio**: el catálogo, las
   variantes de producto, las categorías, la marca, la moneda y el tema visual se controlan por
   **configuración**, no por código. El mismo despliegue sirve para ropa, electrónica, comida, etc.
3. **Dejar una tienda que funciona de verdad de punta a punta** con un **dataset demo** de streetwear y
   tenis (ropa + sneakers), un frontend pulido y el flujo completo de compra verificado.

Se elige **DynamoDB** sobre RDS PostgreSQL porque RDS solo es gratis 12 meses y Lambda+RDS "bien hecho"
exige RDS Proxy (de pago), mientras que Lambda+DynamoDB es la pareja serverless canónica: free tier
permanente, sin VPC ni agotamiento de conexiones, y enseña *single-table design*. El trade-off asumido
es reescribir la capa de datos (se pierden JOINs y Alembic).

> Principio rector: **business-agnostic**. Nada específico de un vertical se hardcodea. La demo de
> ropa/tenis es solo el dataset y la configuración por defecto; cambiar de negocio = cambiar
> configuración + dataset, sin tocar código. Se conserva la marca/estética MetalShop como tema por
> defecto (plata/oro/acero/cobre), pero el tema es configurable.

## What Changes

**Infraestructura / backend (serverless):**

- **BREAKING**: la persistencia pasa de SQLAlchemy/SQLite/PostgreSQL a **DynamoDB single-table**.
  Desaparecen los modelos ORM, las sesiones async de SQLAlchemy y las migraciones Alembic.
- La app FastAPI se empaqueta como **una sola Lambda** ("Lambdalith") vía **Mangum**, expuesta por
  **API Gateway (HTTP API)**. Se elimina el servidor Uvicorn/Gunicorn permanente para producción.
- El **frontend estático** deja de servirse con `StaticFiles` desde FastAPI y pasa a **S3 + CloudFront**.
  La Lambda solo atiende `/api/*`.
- El **rate limiting de login** deja `slowapi` en memoria (no funciona entre invocaciones Lambda) y pasa
  a **throttling de API Gateway**.
- El **email de confirmación** deja SMTP genérico (`fastapi-mail`) y pasa a **Amazon SES**.
- Se introduce **infraestructura como código con AWS SAM** (`template.yaml`).

**Plataforma configurable (business-agnostic):**

- **Modelo de producto genérico**: el producto admite **variantes** con un mapa de **atributos
  arbitrarios** (p. ej. `talla`, `color`, `capacidad`) y stock/precio por variante; un producto puede no
  tener variantes. Nada de campos fijos por vertical.
- Nueva **configuración de tienda** (`store-configuration`): nombre/marca, logo, categorías, moneda,
  idioma/locale, reglas de impuesto y envío, y **tokens de tema** (colores, fuentes) se cargan desde un
  documento de configuración. Cambiar de negocio no requiere recompilar.
- El **frontend** renderiza categorías, variantes y marca de forma **data-driven** desde la config y la
  API; un selector de variante genérico se adapta a los atributos que cada producto declare.

**Producto / datos / frontend (demo + UX):**

- Se crea un **cargador de datos idempotente** que siembra un *dataset intercambiable*; el dataset por
  defecto es **streetwear y tenis** (más un usuario admin de ejemplo) en DynamoDB, reemplazando a
  `seed_products.py`.
- Se **mejora el frontend** (sin frameworks): navegación por categorías configurables, tarjetas con
  selector de variante, galería en el detalle, estados de carga/vacío/error, accesibilidad y responsive
  pulido en los tres breakpoints.
- Se verifica el **flujo completo funcional** (navegar → filtrar → detalle → elegir variante → carrito →
  checkout → confirmación + email → historial; admin: dashboard → CRUD producto → cambiar estado) contra
  el stack serverless con datos sembrados.

La verificación local usa **DynamoDB Local** + **SAM local**; los tests pasan de SQLite in-memory a
DynamoDB Local (o `moto`).

## Capabilities

### New Capabilities
- `serverless-api`: la API FastAPI se ejecuta como Lambda detrás de API Gateway, sin estado y con
  arranque en frío aceptable.
- `dynamodb-persistence`: todos los datos (usuarios, productos con variantes y atributos arbitrarios,
  carrito, pedidos) se persisten en una tabla DynamoDB single-table que cubre todos los patrones de acceso.
- `store-configuration`: la marca, categorías, moneda, locale, impuestos/envío y tema visual se controlan
  por configuración, haciendo la tienda adaptable a cualquier negocio sin cambios de código.
- `static-frontend-cdn`: el frontend estático se sirve desde S3 a través de CloudFront.
- `transactional-email-ses`: el correo de confirmación de pedido se envía mediante Amazon SES.
- `request-throttling`: el endpoint de login se protege con throttling a nivel de API Gateway.
- `iac-sam-deployment`: el stack completo se define y despliega con AWS SAM como infraestructura como código.
- `catalog-seed-data`: un cargador idempotente siembra un dataset demo intercambiable (por defecto
  ropa/tenis) más un admin en DynamoDB.
- `frontend-enhancements`: mejoras de UI data-driven (categorías configurables, selector de variante
  genérico, galería, estados de carga/error, accesibilidad, responsive), sin frameworks.
- `end-to-end-functionality`: el flujo completo de cliente y de admin funciona de extremo a extremo sobre
  el stack serverless con datos sembrados.

### Modified Capabilities
<!-- No existen specs vigentes en openspec/specs/ todavía; este cambio introduce todas las capabilities
     como nuevas. Al archivar, poblará openspec/specs/ con el contrato de la plataforma serverless. -->

## Impact

- **Código backend**: `backend/database.py`, `backend/models/*`, `backend/services/*` (reescritura de la
  capa de acceso a datos a DynamoDB); `backend/main.py` (handler Mangum, quitar `StaticFiles`);
  `backend/limiter.py` y `backend/routers/auth.py` (quitar slowapi); `backend/utils/email.py` (SES);
  `backend/dependencies.py` (cliente DynamoDB en vez de `get_db`); `backend/schemas/product.py`
  (variantes con atributos arbitrarios); `backend/config.py` + nuevo módulo de configuración de tienda.
- **Dependencias** (`pyproject.toml`): +`mangum`, +`boto3`/`aioboto3`; −`alembic`, −`slowapi`,
  −`aiosqlite`; revisar `fastapi-mail` (posible reemplazo por SES SDK).
- **Migraciones**: se elimina `alembic/` y `alembic.ini`.
- **Datos/config**: nuevo `seed_dynamodb.py` (dataset intercambiable; default ropa/tenis) y documento de
  configuración de tienda (marca, categorías, moneda, tema).
- **Infra nueva**: `template.yaml` (SAM), `samconfig.toml`, scripts de despliegue.
- **Frontend**: `index.html`, `product.html`, `css/*` y `js/pages/*` (categorías y variantes data-driven,
  galería, estados); `frontend/js/api.js` (base URL de API Gateway); carga de branding/tema desde config.
- **Tests** (`tests/*`, `tests/conftest.py`): de SQLite in-memory a DynamoDB Local / `moto`; pruebas de
  variantes/atributos, de configuración de tienda y del cargador de datos.
- **Docs**: `README.md`, `PLAN.md`, `docs/backend-standards.md`, nuevo `docs/aws-serverless-standards.md`.
- **Seguridad/IAM**: roles de ejecución de Lambda con permisos mínimos sobre la tabla DynamoDB y SES.
