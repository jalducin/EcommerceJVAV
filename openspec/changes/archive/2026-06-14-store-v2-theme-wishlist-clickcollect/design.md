## Context

Tienda v2 de cara al cliente sobre el API serverless existente. El storefront ya renderiza marca, tema y
categorías desde `GET /api/config` (capability `store-configuration`), el checkout es transaccional
(`backend/repositories/order_repo.py` con `TransactWriteItems`) y el detalle de producto ya muestra un
botón de corazón visual que hoy no persiste nada. Este cambio añade tres mejoras —tema azul metálico por
defecto, wishlist por usuario y click & collect en el checkout— reutilizando esos pilares, sin frameworks
JS/CSS y sin tocar la lógica de negocio más de lo necesario.

## Goals / Non-Goals

**Goals:**
- Cambiar el tema por defecto a una paleta azul metálico suave/profesional vía tokens de tema, manteniendo
  la configuración business-agnostic (cambiar paleta = solo configuración).
- Lista de deseos por usuario autenticado: agregar, quitar y listar productos, persistida en DynamoDB
  single-table; el botón de corazón del detalle la usa.
- Opción "recoger en tienda" en el checkout, con ubicaciones declaradas en la config; envío 0 en pickup;
  el pedido guarda método y ubicación.

**Non-Goals:**
- Compartir o hacer pública la wishlist; mover items de la wishlist al carrito de forma masiva (solo
  enlace simple "agregar al carrito" reusa el flujo existente, no se especifica aquí).
- Gestión de inventario por ubicación de recogida (el stock sigue siendo global por variante; pickup no
  reserva stock por tienda en esta versión).
- Pasarela de pago o reglas de envío avanzadas (multi-tarifa, por zona); el envío sigue siendo el `ship`
  vigente de `store-configuration` salvo que sea pickup (=0).
- Cambiar la identidad metálica para clientes que ya sobrescriben el tema por configuración.

## Decisions

### Decisión 1: Tema azul metálico como tokens por defecto, no como código nuevo
La paleta azul metálico se entrega cambiando los valores por defecto de `StoreConfig.theme` y los tokens
por defecto de `css/variables.css`, no añadiendo lógica. Sigue aplicándose vía CSS Custom Properties desde
`GET /api/config`. Una tienda que ya sobrescribe `theme` en su config conserva su paleta. Sin frameworks
CSS. Paleta propuesta (azul metálico suave/profesional): un azul profundo de marca, un azul acero medio,
un azul claro/acento, una superficie clara casi blanca y un texto oscuro de buen contraste; los nombres de
token se mantienen estables para no romper el CSS (se redefine su valor, no su nombre).

### Decisión 2: Wishlist en el single-table, alineada al patrón de carrito
La wishlist reusa el patrón del carrito: `PK=USER#<id>`, `SK=WISH#<product_id>` (un item por producto, sin
variante). Se añade `keys.wish_sk(product_id)` y `WISH_SK_PREFIX` en `backend/db/keys.py`, un
`wishlist_repo.py` con `add`, `remove`, `list_items` (query por `begins_with(WISH#)`), y un router
`/api/wishlist`. POST es idempotente (re-agregar no duplica); DELETE de algo inexistente no es error
(204/200 idempotente). El listado devuelve los `product_id` guardados; el detalle de cada producto se
resuelve contra el catálogo existente (no se duplica la ficha en la wishlist).

### Decisión 3: `fulfillment` como enum en checkout y pedido, envío resuelto en el backend
`CheckoutRequest` gana `fulfillment: "ship" | "pickup"` (por defecto `ship`, retrocompatible) y
`pickup_location_id: str | None`. El servicio de checkout: si `pickup`, valida que `pickup_location_id`
exista en `store_config.pickup_locations` (si no, 422) y fija `shipping=0`; si `ship`, aplica la regla de
envío vigente. `Order` persiste `fulfillment` y `pickup_location_id` para trazabilidad. La autoridad del
cálculo de envío y de la validación de ubicación es el backend; el cliente nunca fija el envío.

### Decisión 4: `pickup_locations` en `store-configuration`, no en un nuevo store
Las ubicaciones de recogida son configuración de tienda business-agnostic, así que viven en `StoreConfig`
(`pickup_locations: list[PickupLocation]`, cada una con `id`, `name`, `address` y opcionalmente `hours`),
expuestas por `GET /api/config`. El checkout las consume; no se crea un endpoint nuevo solo para listarlas.

### Decisión 5: El botón de corazón es defensa de UX; la autoridad es el JWT del backend
El botón de corazón del detalle alterna llamando a `POST`/`DELETE /api/wishlist`. Solo está activo con
sesión de cliente; sin sesión, invita a iniciar sesión. La pertenencia de la wishlist se deriva del JWT en
el backend (nunca del cliente), de modo que un usuario no puede leer ni mutar la lista de otro.

## Risks / Trade-offs

- **Cambiar tokens por defecto podría afectar contraste/accesibilidad** → elegir la paleta azul con
  contraste suficiente (AA) y verificar en 375/768/1280; mantener estados de carga/vacío/error.
- **Wishlist sin variante** → se guarda por `product_id`; si el producto tiene variantes, "agregar al
  carrito" desde la wishlist aún exige elegir variante en el detalle (no se asume una). Aceptado para v2.
- **Pickup y stock global** → pickup no reserva stock por tienda; riesgo de prometer recogida sin stock
  local. Mitigado declarándolo Non-Goal y manteniendo el descuento de stock transaccional global.
- **Retrocompatibilidad del checkout** → `fulfillment` por defecto `ship`; los clientes/integraciones que
  no lo envían siguen funcionando igual.

## Migration Plan

1. Backend: `pickup_locations` y tema azul por defecto en `store.py`; `fulfillment`/`pickup_location_id` en
   `checkout.py`; `keys.wish_sk`; `wishlist_repo.py`; router `/api/wishlist`; lógica de envío 0 en pickup.
2. Frontend: tokens azul metálico por defecto en `css/variables.css`; botón de corazón conectado a
   `/api/wishlist`; selector de método de entrega y ubicación en el checkout (envío oculto/0 en pickup).
3. Tests unitarios e integración; verificación E2E del agente (wishlist, checkout ship vs pickup, tema).
4. Docs (OpenAPI, standards) y runbook del cliente; validación OpenSpec.

## Open Questions

- ¿La paleta azul exacta (hex de cada token) la define diseño o se fija aquí? (Propuesta: fijar valores por
  defecto razonables con contraste AA y dejarlos sobrescribibles por config.)
- ¿La wishlist debe ofrecer "mover al carrito" en esta versión? (Propuesta: solo enlace al detalle del
  producto; el move-to-cart masivo queda fuera de alcance.)
- ¿`pickup_locations` necesita horarios/zona en v2 o basta `id`+`name`+`address`? (Propuesta: `hours`
  opcional; resto requerido.)
