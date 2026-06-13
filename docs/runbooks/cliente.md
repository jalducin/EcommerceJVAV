# Runbook — Cliente

## Objetivo

Guiar a un cliente registrado por el flujo completo de compra: crear cuenta o iniciar sesión, gestionar el carrito (agregar, actualizar, sincronizar), hacer checkout y consultar sus pedidos. Incluye ejemplos `curl` contra la API en vivo.

## Precondiciones

- API en vivo disponible: `https://cizs8fa7lf.execute-api.us-east-2.amazonaws.com/dev`.
- Catálogo sembrado con productos activos (`GET /api/products` devuelve `items`).
- `curl` y, opcionalmente, `jq` instalados para extraer el token.
- Token JWT **access** para los endpoints de carrito/pedidos (todos requieren `Authorization: Bearer <token>`). El access token vive ~30 min; renueva con el refresh token.

```bash
API="https://cizs8fa7lf.execute-api.us-east-2.amazonaws.com/dev"
```

## Pasos

### 1. Registro (cuenta nueva)

`POST /api/auth/register` — `password` mínimo 6 caracteres; email único.

```bash
curl -s -X POST "$API/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"cliente@example.com","password":"Cliente123!","full_name":"Cliente Demo"}'
```

Respuesta `201` con `UserPublic` (`id`, `email`, `role: "client"`). Si el email ya existe, devuelve `409`.

### 2. Login (obtener tokens)

`POST /api/auth/login` devuelve `access_token` y `refresh_token`.

```bash
TOKEN=$(curl -s -X POST "$API/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"cliente@example.com","password":"Cliente123!"}' | jq -r .access_token)

echo "$TOKEN"
```

Verifica la sesión:

```bash
curl -s "$API/api/auth/me" -H "Authorization: Bearer $TOKEN"
```

### 3. Agregar ítems al carrito

`POST /api/cart/items`. Para productos **con variantes**, usa el `sku` de la variante; para productos sin variantes usa `sku: "-"`.

```bash
# Producto con variante (talla 42 del tenis runner)
curl -s -X POST "$API/api/cart/items" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id":"tenis-runner-metal","sku":"RUNNER-42-NEG","quantity":1}'

# Producto sin variantes (gorra)
curl -s -X POST "$API/api/cart/items" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id":"gorra-copper","sku":"-","quantity":2}'
```

Cada respuesta es el `CartView` recalculado (`lines`, `subtotal`, `tax`, `shipping`, `total`, `currency`).

### 4. Ver / actualizar / eliminar ítems

```bash
# Ver carrito
curl -s "$API/api/cart" -H "Authorization: Bearer $TOKEN"

# Cambiar cantidad de una línea (product_id/sku en la URL)
curl -s -X PUT "$API/api/cart/items/tenis-runner-metal/RUNNER-42-NEG" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"quantity":3}'

# Eliminar una línea
curl -s -X DELETE "$API/api/cart/items/gorra-copper/-" \
  -H "Authorization: Bearer $TOKEN"
```

### 5. Sincronizar el carrito de invitado (sync)

Cuando el cliente venía navegando sin sesión, el carrito local (localStorage) se fusiona al iniciar sesión con `POST /api/cart/sync`.

```bash
curl -s -X POST "$API/api/cart/sync" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"items":[{"product_id":"hoodie-oversize-gold","sku":"HOODIE-M-NEG","quantity":1}]}'
```

### 6. Checkout

`POST /api/orders/checkout`. Toma el carrito actual del usuario, valida stock, calcula totales y crea el pedido (vacía el carrito al terminar).

```bash
curl -s -X POST "$API/api/orders/checkout" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"shipping_address":{"nombre":"Cliente Demo","calle":"Av. Reforma 100","ciudad":"CDMX","cp":"06600"}}'
```

Respuesta `201` con `Order` (`id`, `status: "pending"`, `lines`, `subtotal`, `tax`, `shipping`, `total`).

### 7. Consultar pedidos

```bash
# Historial
curl -s "$API/api/orders" -H "Authorization: Bearer $TOKEN"

# Detalle de un pedido
curl -s "$API/api/orders/<ORDER_ID>" -H "Authorization: Bearer $TOKEN"
```

### 8. Renovar token (cuando expira)

```bash
curl -s -X POST "$API/api/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<REFRESH_TOKEN>"}'
```

## Verificación

- `POST /api/auth/login` devuelve `200` con `access_token` y `refresh_token`; `GET /api/auth/me` responde con tu usuario.
- Tras agregar ítems, `GET /api/cart` muestra las líneas con `total` calculado (incluye `tax` e `shipping` según `GET /api/config`).
- `POST /api/orders/checkout` devuelve `201` y el carrito queda vacío (`GET /api/cart` → `lines: []`).
- El pedido recién creado **aparece** en `GET /api/orders` con su `id` y `status: "pending"`.

## Troubleshooting

| Síntoma | Causa probable | Acción correctiva |
|---|---|---|
| `401 Credenciales inválidas` en login | Email/contraseña incorrectos o usuario inexistente | Verificar credenciales; registrar la cuenta con `POST /api/auth/register`. |
| `401` en carrito/pedidos | Token ausente, mal formado o **expirado** (~30 min) | Reenviar `Authorization: Bearer <token>`; renovar con `POST /api/auth/refresh` o volver a hacer login. |
| `409 El email ya está registrado` | El email ya existe | Iniciar sesión en vez de registrar, o usar otro email. |
| Carrito desincronizado (faltan ítems del invitado) | No se llamó `POST /api/cart/sync` tras login | Ejecutar `sync` con los ítems de localStorage; luego `GET /api/cart` para confirmar la fusión. |
| `400 El carrito está vacío` en checkout | Sin ítems o carrito vaciado por checkout previo | Agregar ítems con `POST /api/cart/items` antes de hacer checkout. |
| `409 Stock insuficiente…` en checkout | Una variante/producto no tiene stock para la cantidad pedida | Reducir cantidad (`PUT /api/cart/items/{id}/{sku}`) o elegir otra variante; revisar stock en `GET /api/products/{id}`. |
| `401 Refresh token inválido` | Refresh token expirado (~7 días) o de tipo incorrecto | Volver a iniciar sesión con `POST /api/auth/login`. |
