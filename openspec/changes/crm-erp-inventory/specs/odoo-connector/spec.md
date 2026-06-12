## ADDED Requirements

### Requirement: Adapter de Odoo sobre el connector framework

El conector de Odoo SHALL implementar la interfaz de adapter y declarar las capacidades `inventario` y,
donde aplique, `pedidos`. La autenticación SHALL usar la API JSON-RPC de Odoo con credenciales en el vault.
Es ejecutable con Odoo **community/local**.

#### Scenario: Inventario sincronizado con Odoo vía JSON-RPC

- **WHEN** se sincroniza inventario entre el canónico y Odoo
- **THEN** el adapter usa JSON-RPC para leer/escribir niveles de stock resolviendo el mapeo de IDs
- **AND** la operación es idempotente y respeta las reglas de fuente de verdad

#### Scenario: Pedido reflejado en Odoo (cuando aplique)

- **WHEN** un pedido canónico debe registrarse en Odoo
- **THEN** el adapter crea el documento correspondiente sin duplicar por el mapeo de IDs
