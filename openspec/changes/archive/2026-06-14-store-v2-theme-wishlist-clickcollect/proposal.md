## Why

JV Market (MetalShop) ya tiene storefront, checkout transaccional y panel de administración sobre el API
serverless, pero la experiencia de tienda v2 pide tres mejoras de cara al cliente que hoy no existen:

1. **Identidad visual por defecto desactualizada**: el tema por defecto es la paleta metálica original
   (plata/oro/acero/cobre), de aspecto duro. La tienda v2 quiere una identidad **azul metálico** suave y
   profesional, aplicada solo vía tokens de tema (sin frameworks, sin recompilar lógica).
2. **No hay lista de deseos**: el botón de corazón del detalle de producto no persiste nada; el cliente
   autenticado no puede guardar productos para después.
3. **Solo hay envío a domicilio**: el checkout asume entrega por paquetería; no existe la opción de
   **recoger en tienda** (click & collect), pese a que la configuración de tienda es business-agnostic y
   podría declarar ubicaciones de recogida.

Este cambio entrega las tres mejoras como capa de cliente sobre el stack existente, reutilizando
`store-configuration` (tokens de tema y ubicaciones de recogida), el JWT de cliente y el checkout
transaccional, sin introducir frameworks JS/CSS.

## What Changes

- **Tema azul metálico por defecto**: el tema por defecto de `store-configuration` pasa a una paleta azul
  metálica suave/profesional, aplicada vía CSS Custom Properties. Sigue siendo configurable; cambiar de
  paleta es solo configuración. Sin frameworks CSS.
- **Lista de deseos (wishlist) por usuario autenticado**: nuevos endpoints `GET/POST/DELETE /api/wishlist`
  para listar, agregar y quitar productos de la lista de deseos. Persistencia en DynamoDB (single-table,
  `PK=USER#<id>`, `SK=WISH#<product_id>`). El botón de corazón del detalle de producto usa estos endpoints.
- **Click & collect (recoger en tienda) en el checkout**: `store-configuration` define `pickup_locations`
  (ubicaciones de recogida). El checkout acepta `fulfillment` = `ship` | `pickup` y, cuando es `pickup`, un
  `pickup_location_id`. El pedido guarda el método de entrega y la ubicación. Cuando es `pickup` **no se
  cobra envío** (envío = 0).

## Capabilities

### New Capabilities

- `wishlist`: lista de deseos por usuario autenticado (agregar/quitar/listar productos), persistida en
  DynamoDB (`PK=USER#<id>`, `SK=WISH#<product_id>`), expuesta por `GET/POST/DELETE /api/wishlist` y usada por
  el botón de corazón del detalle de producto.
- `click-and-collect`: opción de entrega "recoger en tienda" en el checkout, con ubicaciones declaradas en
  `store-configuration` (`pickup_locations`), método `fulfillment` (`ship` | `pickup`) y `pickup_location_id`
  en el checkout y en el pedido, con envío en 0 para recogida.

### Modified Capabilities

- `store-configuration`: el tema visual por defecto pasa a una paleta **azul metálico** suave/profesional
  (manteniéndolo configurable y sin frameworks), y la configuración de tienda incorpora la lista de
  **ubicaciones de recogida** (`pickup_locations`) consumida por el flujo de click & collect.

## Impact

- **Dependencias**: requiere el Sprint 0 (`migrate-to-serverless-aws`: API serverless, `store-configuration`,
  DynamoDB single-table, JWT de cliente, checkout transaccional) y la base de frontend
  (`frontend-enhancements`, detalle de producto con botón de corazón). No depende del panel admin.
- **Backend**:
  - `backend/schemas/store.py`: `StoreConfig.theme` por defecto azul metálico; nuevo campo
    `pickup_locations: list[PickupLocation]`.
  - `backend/schemas/checkout.py`: `CheckoutRequest` gana `fulfillment` y `pickup_location_id`; `Order` gana
    `fulfillment` y `pickup_location_id`.
  - Nuevo `backend/schemas/wishlist.py` (item/listado) y `backend/repositories/wishlist_repo.py`
    (`PK=USER#<id>`, `SK=WISH#<product_id>`); helper de clave en `backend/db/keys.py` (`wish_sk`).
  - Nuevo `backend/routers/wishlist.py` con `GET/POST/DELETE /api/wishlist` bajo el JWT de cliente.
  - Servicio de checkout: si `fulfillment=pickup` valida `pickup_location_id` contra la config y fija
    envío en 0; si `fulfillment=ship` mantiene la regla de envío vigente.
- **Frontend**: `css/variables.css` (tokens azul metálico por defecto, sin colores hardcodeados); detalle de
  producto (botón de corazón conectado a `/api/wishlist` con estados de carga/vacío/error); checkout
  (selector de método de entrega y de ubicación de recogida, ocultar/0 envío en pickup). Sin frameworks.
- **Tests**: pruebas unitarias del `wishlist_repo` y del servicio de checkout (pickup vs ship, envío 0,
  ubicación inválida); pruebas de integración de los endpoints `/api/wishlist` (200 autenticado, 401 sin
  token, idempotencia de POST/DELETE) y del checkout con `fulfillment`.
- **Docs**: contrato OpenAPI de `/api/wishlist` y del checkout con `fulfillment`; `docs/backend-standards.md`
  (claves DynamoDB de wishlist), `docs/frontend-standards.md` (tema azul, botón de corazón); runbook del
  cliente en `docs/runbooks/`.
- **Seguridad**: la wishlist es por usuario autenticado; nunca se exponen las listas de otro usuario. El
  cálculo de envío y la validación de la ubicación de recogida son autoridad del backend (no del cliente).
