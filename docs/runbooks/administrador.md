# Runbook — Administrador

## Objetivo

Operar el panel de administración de MetalShop: gestionar el catálogo con variantes (crear, editar, desactivar productos), revisar el dashboard de métricas, consultar los pedidos unificados de todos los canales y revisar el estado de los conectores de integración.

## Precondiciones

- API en vivo: `https://cizs8fa7lf.execute-api.us-east-2.amazonaws.com/dev`.
- Frontend (panel) en CloudFront: `https://d3rw1q49m6mvnq.cloudfront.net/admin/`.
- Una cuenta con **rol `admin`**. La cuenta sembrada por defecto es `admin@metalshop.mx` / `Admin123!`.
- Token JWT **access** de esa cuenta admin. Todos los endpoints `/api/admin/*` y los de escritura de catálogo (`POST/PUT/DELETE /api/products`) requieren `Authorization: Bearer <token>` de un usuario admin; sin rol admin devuelven `403`.

```bash
API="https://cizs8fa7lf.execute-api.us-east-2.amazonaws.com/dev"
```

## Pasos

### 1. Login como administrador

```bash
TOKEN=$(curl -s -X POST "$API/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@metalshop.mx","password":"Admin123!"}' | jq -r .access_token)
```

En el navegador, inicia sesión y entra al panel: `https://d3rw1q49m6mvnq.cloudfront.net/admin/dashboard.html` (secciones bajo `/admin/*`: dashboard, productos, pedidos).

### 2. Dashboard de métricas

```bash
curl -s "$API/api/admin/dashboard" -H "Authorization: Bearer $TOKEN"
```

Devuelve métricas agregadas (ventas, pedidos pendientes, bajo stock, etc.) que alimentan `/admin/dashboard.html`.

### 3. Crear un producto con variantes

`POST /api/products`. La `category` debe existir en `GET /api/config` (`tenis`, `ropa`, `accesorios`); en caso contrario devuelve `422`. Cada variante lleva `sku`, `attrs` (atributos arbitrarios), `stock` y `price_delta` opcional.

```bash
curl -s -X POST "$API/api/products" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
        "name":"Tenis Forge Steel",
        "description":"Sneakers premium edición acero.",
        "price":2199.0,
        "category":"tenis",
        "images":["https://picsum.photos/seed/forge/600"],
        "variants":[
          {"sku":"FORGE-42-NEG","attrs":{"talla":"42","color":"negro"},"stock":5},
          {"sku":"FORGE-43-NEG","attrs":{"talla":"43","color":"negro"},"stock":3,"price_delta":50.0}
        ]
      }'
```

Respuesta `201` con el `Product` creado (incluye `id` y `created_at`). Para un producto **sin** variantes, omite `variants` y usa `stock` a nivel de producto.

### 4. Editar un producto

`PUT /api/products/{id}` (actualización parcial). Para reemplazar las variantes, envía el arreglo `variants` completo.

```bash
curl -s -X PUT "$API/api/products/tenis-forge-steel" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"price":1999.0}'
```

### 5. Desactivar / eliminar un producto

```bash
# Desactivar (soft, vía update): deja de aparecer al visitante
curl -s -X PUT "$API/api/products/tenis-forge-steel" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_active":false}'

# Eliminar
curl -s -X DELETE "$API/api/products/tenis-forge-steel" \
  -H "Authorization: Bearer $TOKEN" -i
```

`DELETE` devuelve `204` sin cuerpo; `404` si el producto no existe.

### 6. Pedidos unificados (todos los canales)

```bash
# Listar pedidos de todos los canales (web + conectores)
curl -s "$API/api/admin/orders" -H "Authorization: Bearer $TOKEN"

# Cambiar el estado de un pedido de canal por su id canónico
curl -s -X PATCH "$API/api/admin/orders/channel/<CANONICAL_ID>/status?new_status=shipped" \
  -H "Authorization: Bearer $TOKEN"
```

### 7. Conectores de integración

```bash
curl -s "$API/api/admin/connectors" -H "Authorization: Bearer $TOKEN"
```

Devuelve la lista de conectores con `name`, `category` (canal, marketplace, social, feed, crm, erp, inventario, pos, pago), `capabilities`, `deferred` y `status` (`disponible` o `deuda_tecnica`). La rotación de credenciales del vault la hace el operador (ver `operador-devops.md`).

## Verificación

- `GET /api/admin/dashboard` responde `200` solo con token admin (con token de cliente: `403`).
- Tras crear un producto, aparece en `GET /api/products` y `GET /api/products/{id}` devuelve sus variantes.
- Tras `is_active:false`, el producto **deja de aparecer** para el visitante (`GET /api/products/{id}` → `404`).
- `PATCH …/orders/channel/{id}/status` devuelve `{"id":…,"status":…}` y el cambio se refleja en `GET /api/admin/orders`.
- `GET /api/admin/connectors` lista los conectores con su `status`; los marcados `deuda_tecnica` figuran como `deferred: true`.

## Troubleshooting

| Síntoma | Causa probable | Acción correctiva |
|---|---|---|
| `403` en `/api/admin/*` o al crear/editar producto | Token de usuario **sin rol admin** (o ausente) | Iniciar sesión con una cuenta admin (`admin@metalshop.mx`); confirmar el rol con `GET /api/auth/me` (`role: "admin"`). |
| `401` en el panel | Token expirado (~30 min) | Renovar con `POST /api/auth/refresh` o volver a hacer login. |
| `422 Categoría inválida: <x>` al crear/editar | La `category` no está en `GET /api/config.categories` | Usar una categoría existente o añadirla a la configuración de tienda antes de crear el producto. |
| `404 Producto no encontrado` en PUT/DELETE | `product_id` incorrecto | Confirmar el `id` con `GET /api/products`. |
| Conector aparece pero no sincroniza | Conector marcado `deferred`/`deuda_tecnica`, o **sin credenciales** en el vault | Confirmar `status` en `GET /api/admin/connectors`; cargar/rotar el secreto `metalshop/connectors/<conector>` (ver `operador-devops.md`). |
| Dashboard sin datos | Sin pedidos o tabla recién sembrada | Generar pedidos de prueba (flujo de `cliente.md`) y recargar. |
