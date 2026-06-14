# wishlist Specification

## Purpose
TBD - created by archiving change store-v2-theme-wishlist-clickcollect. Update Purpose after archive.
## Requirements
### Requirement: Lista de deseos por usuario autenticado

El sistema SHALL exponer una lista de deseos (wishlist) por usuario autenticado, accesible solo con un JWT
de cliente válido, que permita agregar, quitar y listar productos. La pertenencia de la wishlist SHALL
derivarse del usuario del JWT en el backend; un usuario NO SHALL poder leer ni mutar la lista de otro
usuario. Las solicitudes sin sesión válida SHALL responder 401.

#### Scenario: Usuario autenticado lista su wishlist

- **WHEN** un cliente autenticado solicita `GET /api/wishlist`
- **THEN** la respuesta 200 incluye los productos que el cliente ha guardado
- **AND** una wishlist sin productos devuelve una lista vacía, no un error

#### Scenario: Acceso sin sesión

- **WHEN** se solicita `GET /api/wishlist` sin un JWT de cliente válido
- **THEN** el backend responde 401
- **AND** no expone ninguna wishlist

#### Scenario: Aislamiento entre usuarios

- **WHEN** un cliente autenticado consulta o modifica la wishlist
- **THEN** solo opera sobre los productos guardados por su propio usuario (derivado del JWT)
- **AND** nunca accede a los productos guardados por otro usuario

### Requirement: Agregar y quitar productos de la wishlist

El sistema SHALL exponer `POST /api/wishlist` para agregar un producto a la wishlist del usuario y
`DELETE /api/wishlist` (o `DELETE /api/wishlist/{product_id}`) para quitarlo. Ambas operaciones SHALL ser
idempotentes: agregar un producto ya presente no SHALL duplicarlo, y quitar un producto ausente no SHALL
ser un error. La persistencia SHALL usar DynamoDB single-table con clave `PK=USER#<id>` y
`SK=WISH#<product_id>` (un ítem por producto, sin variante).

#### Scenario: Agregar un producto a la wishlist

- **WHEN** un cliente autenticado envía `POST /api/wishlist` con un `product_id`
- **THEN** el producto queda guardado con clave `PK=USER#<id>` y `SK=WISH#<product_id>`
- **AND** aparece en el siguiente `GET /api/wishlist`

#### Scenario: Agregar un producto ya presente es idempotente

- **WHEN** un cliente agrega un producto que ya está en su wishlist
- **THEN** la wishlist no duplica el producto
- **AND** la operación responde con éxito sin error

#### Scenario: Quitar un producto de la wishlist

- **WHEN** un cliente autenticado envía `DELETE` del producto sobre su wishlist
- **THEN** el producto deja de aparecer en `GET /api/wishlist`
- **AND** quitar un producto que no estaba presente responde con éxito (idempotente), no con error

### Requirement: Botón de corazón del detalle de producto conectado a la wishlist

El botón de corazón de la página de detalle de producto SHALL usar los endpoints de wishlist para alternar
el producto: agregarlo si no está y quitarlo si ya está, reflejando el estado actual. El botón SHALL
manejar los estados de carga y error sin pantallas en blanco. Sin sesión de cliente, el botón NO SHALL
mutar nada y SHALL invitar a iniciar sesión. No SHALL introducir frameworks JS.

#### Scenario: Alternar el corazón con sesión

- **WHEN** un cliente autenticado pulsa el botón de corazón en el detalle de un producto no guardado
- **THEN** el frontend llama a `POST /api/wishlist` y marca el corazón como activo
- **AND** al pulsarlo de nuevo llama a `DELETE` y lo desmarca

#### Scenario: Botón de corazón sin sesión

- **WHEN** un visitante sin sesión pulsa el botón de corazón
- **THEN** no se realiza ninguna mutación de wishlist
- **AND** se invita a iniciar sesión

#### Scenario: Estado de error al alternar

- **WHEN** la llamada a la wishlist falla
- **THEN** el botón muestra un estado de error accionable y no queda en un estado inconsistente
- **AND** no se produce un error de consola sin manejar

