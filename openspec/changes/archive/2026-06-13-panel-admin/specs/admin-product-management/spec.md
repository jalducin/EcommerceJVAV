## ADDED Requirements

### Requirement: Crear y editar productos con variantes desde la UI

La UI de administración SHALL permitir crear y editar productos sobre `POST /api/products` y `PUT /api/products/{id}`, incluyendo variantes con un mapa de **atributos arbitrarios** (por ejemplo talla, color, capacidad) y precio/stock por variante; un producto MAY no tener variantes.

#### Scenario: Crear un producto con dos variantes

- **WHEN** el admin completa el formulario con un producto y dos variantes con atributos arbitrarios y stock
- **THEN** la UI envía `POST /api/products` con las variantes y atributos declarados
- **AND** al recibir 201 muestra el producto creado en la lista

#### Scenario: Editar las variantes de un producto

- **WHEN** el admin modifica precio o stock de una variante existente y guarda
- **THEN** la UI envía `PUT /api/products/{id}` con las variantes actualizadas
- **AND** refleja el producto actualizado tras la respuesta 200

### Requirement: Validación de categoría contra la configuración de tienda

La UI SHALL validar la categoría del producto contra las categorías declaradas en `store-config` y manejar el 422 del backend cuando la categoría es inválida, mostrando un error de validación junto al campo correspondiente.

#### Scenario: Categoría no permitida

- **WHEN** el admin intenta guardar un producto con una categoría que no existe en la configuración de tienda
- **THEN** el backend responde 422 y la UI muestra el error junto al campo categoría
- **AND** no limpia el resto del formulario

#### Scenario: Selector de categoría poblado desde la config

- **WHEN** se abre el formulario de producto
- **THEN** el selector de categoría se puebla desde `GET /api/config`
- **AND** solo ofrece categorías válidas

### Requirement: Soft delete de productos

La UI SHALL desactivar productos mediante `DELETE /api/products/{id}` (soft delete que marca `is_active=false`), de modo que los productos desactivados dejen de aparecer en el storefront pero permanezcan accesibles para el administrador.

#### Scenario: Desactivar un producto

- **WHEN** el admin confirma la desactivación de un producto
- **THEN** la UI envía `DELETE /api/products/{id}` y al recibir 204 marca el producto como inactivo en la lista admin
- **AND** el producto deja de listarse en el storefront público

#### Scenario: Producto inexistente

- **WHEN** se intenta desactivar un producto que no existe
- **THEN** el backend responde 404 y la UI muestra un mensaje de "producto no encontrado"
- **AND** refresca la lista para reflejar el estado real
