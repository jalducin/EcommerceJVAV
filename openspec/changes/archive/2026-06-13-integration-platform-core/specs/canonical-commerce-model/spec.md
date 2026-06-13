## ADDED Requirements

### Requirement: Modelo canónico independiente de proveedor

El sistema SHALL definir un modelo de dominio canónico —Producto, Variante, NivelDeInventario, Pedido,
Cliente, Pago y Fulfillment— que NO SHALL contener campos ni semántica específicos de un proveedor
externo. Todo conector SHALL traducir entre el modelo del proveedor y este modelo canónico.

#### Scenario: Pedido de dos canales distintos en forma canónica

- **WHEN** llega un pedido desde Shopify y otro desde MercadoLibre
- **THEN** ambos se representan con la misma estructura de Pedido canónico
- **AND** ningún campo del modelo canónico es específico de Shopify o MercadoLibre

#### Scenario: Producto canónico con variantes y atributos arbitrarios

- **WHEN** se modela un producto con variantes (atributos arbitrarios) y niveles de inventario
- **THEN** se reutiliza el modelo de variantes business-agnostic del Sprint 0
- **AND** el inventario se expresa como NivelDeInventario por variante/ubicación

### Requirement: Mapeo de identificadores externos a canónicos

El sistema SHALL mantener un mapeo persistente entre el identificador canónico de cada entidad y su
identificador en cada proveedor (por conector). El mapeo SHALL ser consultable en ambos sentidos
(canónico→externo y externo→canónico).

#### Scenario: Resolver el id externo de un producto para un canal

- **WHEN** se va a sincronizar un producto canónico hacia Shopify
- **THEN** el sistema resuelve el id de Shopify desde el mapeo
- **AND** si no existe, lo crea y registra la correspondencia

#### Scenario: Resolver el id canónico de un pedido entrante

- **WHEN** entra un webhook de pedido con un id externo conocido
- **THEN** el sistema resuelve el pedido canónico correspondiente desde el mapeo
- **AND** evita crear un duplicado del pedido
