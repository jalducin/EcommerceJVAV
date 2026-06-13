# Runbook — Visitante

## Objetivo

Permitir que cualquier persona, **sin sesión**, navegue el catálogo de MetalShop: liste productos, filtre por categoría, busque por texto y vea el detalle de un producto con sus variantes. Solo lectura.

## Precondiciones

- Stack `metalshop-dev` desplegado y respondiendo (ver `operador-devops.md`).
- Tabla `metalshop-dev` sembrada con configuración y productos activos (`seed_dynamodb.py`).
- Navegador con acceso a internet. **No se requiere autenticación** ni token.
- Endpoints públicos disponibles:
  - Storefront: `https://d3rw1q49m6mvnq.cloudfront.net`
  - API: `GET /api/config`, `GET /api/products`, `GET /api/products/{id}`

## Pasos

### 1. Abrir el storefront

Navega a `https://d3rw1q49m6mvnq.cloudfront.net`. La página de catálogo carga la configuración de tienda (`GET /api/config`) y el listado inicial de productos (`GET /api/products`).

### 2. Listar el catálogo (API directa, opcional)

```bash
API="https://cizs8fa7lf.execute-api.us-east-2.amazonaws.com/dev"

# Listado por defecto (limit=12, offset=0)
curl -s "$API/api/products"

# Paginación: segunda página de 6 en 6
curl -s "$API/api/products?limit=6&offset=6"
```

Respuesta: objeto `ProductList` con `items`, `total`, `limit`, `offset`.

### 3. Filtrar por categoría

Categorías sembradas por defecto: `tenis`, `ropa`, `accesorios`.

```bash
curl -s "$API/api/products?category=tenis"
```

### 4. Buscar por texto

El parámetro `q` busca por texto (nombre/descripción). En el storefront, el buscador aplica debounce de 300 ms.

```bash
curl -s "$API/api/products?q=hoodie"
```

### 5. Filtrar por rango de precio (opcional)

```bash
curl -s "$API/api/products?min_price=500&max_price=2000"
```

### 6. Ver detalle de un producto y sus variantes

```bash
curl -s "$API/api/products/tenis-runner-metal"
```

Respuesta: objeto `Product` con `variants` (cada variante con `sku`, `attrs` como `{"talla":"42","color":"negro"}`, `stock` y `price_delta`). En el storefront se abre la página de detalle con galería y selector de variante.

## Verificación

- `GET /api/config` devuelve `200` con `name`, `categories`, `currency` (`MXN`), etc.
- `GET /api/products` devuelve `200` con `total > 0` y `items` poblado, **sin enviar token**.
- Todos los productos listados están **activos**: `GET /api/products/{id}` de un producto inactivo o inexistente devuelve `404`.
- El filtro `category=tenis` devuelve solo productos de esa categoría; `q=hoodie` reduce el conjunto.
- En el navegador, las tarjetas de producto se renderizan y el detalle muestra variantes seleccionables.

## Troubleshooting

| Síntoma | Causa probable | Acción correctiva |
|---|---|---|
| Catálogo vacío (`items: []`, `total: 0`) | Tabla sin sembrar o sembrada en otra tabla/región | Ejecutar el seed: `DYNAMODB_TABLE=metalshop-dev python seed_dynamodb.py --no-create-table` (ver `operador-devops.md`). |
| El storefront carga pero no aparecen productos | Frontend desplegado apuntando a otra API, o caché de CloudFront servida con datos viejos | Verificar `GET /api/products` directo a la API; invalidar CloudFront (`/*`) tras republicar el frontend. |
| Error de carga / pantalla en blanco | Objetos no subidos a S3 o invalidación pendiente de CloudFront | Republicar frontend a S3 e invalidar la distribución `E3J6D06L3SRBXS` (ver `operador-devops.md`). |
| `404` al abrir un producto | `product_id` inexistente o producto inactivo (soft-delete) | Confirmar el `id` con `GET /api/products`; los inactivos no se exponen al visitante. |
| Error CORS en el navegador | Origen no permitido en la configuración del API Gateway/app | Verificar `FRONTEND_URL`/CORS del stack; en `dev` se permite `*`. |
| `5xx` desde la API | Lambda con error o cold start fallido | Revisar logs en CloudWatch `/aws/lambda/metalshop-api-dev` (ver `operador-devops.md`). |
