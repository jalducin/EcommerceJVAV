# admin-product-management Specification

## Purpose
TBD - created by archiving change panel-admin. Update Purpose after archive.
## Requirements
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

### Requirement: Gestión de categorías de la tienda desde el panel admin

El panel admin SHALL permitir al administrador **listar, agregar y eliminar** las categorías de la tienda
sobre endpoints admin (`GET/POST /api/admin/categories`, `DELETE /api/admin/categories/{name}`) que
persisten en `store-config.categories`. Agregar SHALL ser idempotente y sin duplicados (insensible a
mayúsculas/minúsculas y con recorte de espacios); eliminar una categoría **en uso por algún producto
activo** SHALL rechazarse con 409 y un mensaje claro, sin modificar la configuración. Tras cualquier
cambio, el selector de categoría del formulario de producto SHALL reflejar la lista actualizada.

#### Scenario: Agregar una categoría

- **WHEN** el admin agrega una categoría nueva desde el panel
- **THEN** la UI envía `POST /api/admin/categories` con el nombre y al recibir 201 la categoría aparece en el listado
- **AND** el selector de categoría del formulario de producto la ofrece como opción válida

#### Scenario: Agregar una categoría duplicada es idempotente

- **WHEN** el admin agrega una categoría cuyo nombre ya existe (ignorando mayúsculas y espacios)
- **THEN** el backend no la duplica y la lista de categorías permanece sin entradas repetidas
- **AND** la UI muestra la categoría existente sin error fatal

#### Scenario: Eliminar una categoría en uso

- **WHEN** el admin intenta eliminar una categoría asignada a uno o más productos activos
- **THEN** el backend responde 409 y la configuración de categorías no cambia
- **AND** la UI muestra que la categoría está en uso y no puede eliminarse

#### Scenario: Eliminar una categoría sin uso

- **WHEN** el admin elimina una categoría que ningún producto activo utiliza
- **THEN** la UI envía `DELETE /api/admin/categories/{name}` y al recibir 204 la categoría desaparece del listado
- **AND** el selector de categoría deja de ofrecerla

### Requirement: Galería de múltiples imágenes por producto

El panel admin SHALL permitir gestionar **varias imágenes por producto** como una galería ordenada
(`images: list[str]`), donde la **primera** imagen es la principal. La UI SHALL permitir **agregar**
imágenes (por subida de archivo o por URL), **quitarlas** y **reordenarlas**, y enviar el arreglo
resultante en `POST /api/products` y `PUT /api/products/{id}`. Un producto MAY no tener imágenes.

#### Scenario: Agregar varias imágenes y definir la principal

- **WHEN** el admin agrega dos o más imágenes a un producto y deja una en primer lugar
- **THEN** la UI envía `images` con el orden elegido y la primera se usa como imagen principal
- **AND** la lista y la ficha de producto muestran esa imagen como principal

#### Scenario: Quitar una imagen de la galería

- **WHEN** el admin quita una imagen de la galería y guarda
- **THEN** la UI envía `PUT /api/products/{id}` con el arreglo `images` sin esa imagen
- **AND** la imagen deja de mostrarse en el storefront tras la respuesta 200

#### Scenario: Compatibilidad con productos de una sola imagen

- **WHEN** se edita un producto creado con una única imagen
- **THEN** la galería la muestra como principal sin pérdida de datos
- **AND** el admin puede agregar más imágenes sin romper la existente

