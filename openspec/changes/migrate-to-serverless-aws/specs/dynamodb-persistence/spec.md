## ADDED Requirements

### Requirement: Persistencia en DynamoDB single-table

Todos los datos del dominio (usuarios, productos, carrito, pedidos) SHALL persistirse en una única tabla
DynamoDB con clave compuesta (partition key + sort key) y los índices secundarios globales (GSI)
necesarios para cubrir los patrones de acceso. El código de acceso a datos SHALL usar exclusivamente la
API de DynamoDB (boto3/aioboto3); NO SHALL quedar dependencia de SQLAlchemy, Alembic ni SQLite.

#### Scenario: Lectura de una entidad por su clave

- **WHEN** el servicio solicita un producto por su id
- **THEN** se ejecuta un `GetItem` por la clave del producto
- **AND** devuelve el item o `None` si no existe

#### Scenario: Sin dependencias relacionales residuales

- **WHEN** se inspeccionan las dependencias del proyecto tras la migración
- **THEN** `sqlalchemy`, `alembic` y `aiosqlite` no aparecen como dependencias de runtime

### Requirement: Producto con variantes y atributos arbitrarios (business-agnostic)

El modelo de producto SHALL soportar cero o más **variantes**, cada una con un mapa de **atributos
arbitrarios** (clave→valor, p. ej. `talla`/`color`/`capacidad`), su propio **stock** y un ajuste de
precio opcional. El modelo NO SHALL hardcodear atributos específicos de un vertical. Un producto sin
variantes SHALL gestionar el stock a nivel de producto.

#### Scenario: Producto con variantes de talla y color

- **WHEN** se crea un producto con variantes `[{talla:42,color:negro,stock:5},{talla:43,color:negro,stock:0}]`
- **THEN** el producto se persiste con sus variantes y stock por variante
- **AND** la API expone los atributos de cada variante sin nombres de campo fijos por vertical

#### Scenario: Producto sin variantes

- **WHEN** se crea un producto sin variantes con `stock: 10`
- **THEN** el stock se gestiona a nivel de producto
- **AND** el checkout valida disponibilidad contra ese stock

### Requirement: Patrones de acceso cubiertos por el diseño

El diseño single-table SHALL cubrir, mediante claves o GSIs, todos los patrones de acceso actuales:
obtener usuario por email (login) y por id; listar productos con filtro por categoría, búsqueda por
nombre y rango de precio con paginación; obtener producto por id; carrito por usuario; crear pedido;
listar pedidos por usuario; obtener detalle de pedido; listar todos los pedidos (admin) con filtro por
estado; y las métricas de dashboard (ventas del día, pedidos pendientes, productos con stock bajo).

#### Scenario: Login busca usuario por email

- **WHEN** un usuario inicia sesión con su email
- **THEN** se consulta el GSI de email para localizar al usuario
- **AND** se valida la contraseña con el hash almacenado

#### Scenario: Listado de productos por categoría con paginación

- **WHEN** el catálogo pide productos de la categoría `tenis` con límite 12
- **THEN** se consulta el GSI de categoría devolviendo hasta 12 items
- **AND** se devuelve un token/offset para la siguiente página

#### Scenario: Pedidos de un usuario

- **WHEN** un usuario autenticado pide su historial
- **THEN** se hace `Query` por su partition key con `begins_with(SK, "ORDER#")`
- **AND** devuelve sus pedidos ordenados por fecha

### Requirement: Checkout transaccional y descuento de inventario

El checkout SHALL crear el pedido y descontar el inventario de cada item/variante de forma atómica usando
`TransactWriteItems` con una condición que impida vender por debajo de cero. Si el stock es insuficiente,
la transacción SHALL fallar sin crear el pedido ni descontar inventario.

#### Scenario: Checkout con stock suficiente

- **WHEN** se hace checkout de items con stock disponible
- **THEN** la transacción crea el pedido y descuenta el stock de cada variante
- **AND** devuelve el id del pedido

#### Scenario: Checkout con stock insuficiente

- **WHEN** se hace checkout de una variante con stock 0
- **THEN** la transacción falla con error de condición
- **AND** no se crea pedido ni se modifica inventario alguno
