# admin-order-management Specification

## Purpose
TBD - created by archiving change panel-admin. Update Purpose after archive.
## Requirements
### Requirement: Listado unificado de pedidos para admin

El sistema SHALL exponer `GET /api/admin/orders`, protegido con `require_admin`, que devuelve los pedidos del storefront y los pedidos canónicos de canales externos en una lista unificada, indicando el canal de origen de cada pedido y permitiendo filtrar por estado y por canal.

#### Scenario: Admin lista todos los pedidos

- **WHEN** un admin autenticado solicita `GET /api/admin/orders`
- **THEN** la respuesta 200 incluye pedidos del storefront y de canales externos con su canal de origen
- **AND** cada pedido muestra estado, total y fecha

#### Scenario: Filtrar por canal

- **WHEN** el admin solicita `GET /api/admin/orders` filtrando por un canal específico
- **THEN** la respuesta solo incluye pedidos de ese canal
- **AND** un filtro sin coincidencias devuelve una lista vacía, no un error

#### Scenario: Acceso sin rol admin

- **WHEN** un usuario sin rol admin solicita `GET /api/admin/orders`
- **THEN** el backend responde 403
- **AND** no expone ningún pedido

### Requirement: Cambio de estado de un pedido desde la UI

El sistema SHALL exponer un endpoint admin para cambiar el estado de un pedido (por ejemplo de `pending` a `shipped` o `cancelled`), protegido con `require_admin`, validando que la transición de estado sea permitida y devolviendo el pedido actualizado.

#### Scenario: Cambiar estado a enviado

- **WHEN** el admin cambia el estado de un pedido pendiente a enviado
- **THEN** el endpoint actualiza el estado y devuelve el pedido con el nuevo estado
- **AND** la lista de pedidos refleja el cambio

#### Scenario: Transición de estado inválida

- **WHEN** el admin solicita una transición de estado no permitida
- **THEN** el backend responde 422 con el motivo
- **AND** el estado del pedido no cambia

#### Scenario: Pedido inexistente

- **WHEN** se intenta cambiar el estado de un pedido que no existe
- **THEN** el backend responde 404
- **AND** la UI muestra un mensaje de "pedido no encontrado"

