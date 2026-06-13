# connector-framework Specification

## Purpose
TBD - created by archiving change integration-platform-core. Update Purpose after archive.
## Requirements
### Requirement: Interfaz de adapter con capacidades declaradas

El sistema SHALL definir una interfaz de **adapter** común que cada conector implemente. Cada conector
SHALL declarar sus **capacidades** soportadas (p. ej. catálogo, inventario, pedidos, clientes, pagos,
fulfillment). El núcleo SHALL invocar únicamente las capacidades que el conector declare soportar.

#### Scenario: Conector que solo soporta catálogo e inventario

- **WHEN** un conector declara soportar `catalogo` e `inventario` pero no `pedidos`
- **THEN** el núcleo le delega sync de catálogo e inventario
- **AND** no le solicita operaciones de pedidos

#### Scenario: Alta de un conector nuevo sin tocar el núcleo

- **WHEN** se agrega un adapter nuevo que implementa la interfaz y se registra
- **THEN** queda disponible para sincronización
- **AND** no se modifica código del núcleo ni de otros conectores

### Requirement: Registro y configuración de conectores

El sistema SHALL mantener un **registro de conectores** habilitados por configuración. Habilitar o
deshabilitar un conector SHALL ser una operación de configuración, sin redeploy de código.

#### Scenario: Habilitar un conector por configuración

- **WHEN** se habilita el conector de WooCommerce en la configuración
- **THEN** el registro lo expone como activo
- **AND** el motor de sincronización empieza a considerarlo

### Requirement: Vault de credenciales y OAuth

Las credenciales y tokens de cada conector SHALL almacenarse en AWS Secrets Manager, nunca en el código ni
en la tabla de datos del dominio. Para proveedores OAuth, el sistema SHALL soportar el flujo de
autorización y el **refresh automático** de tokens expirados.

#### Scenario: Token expirado se renueva automáticamente

- **WHEN** una llamada a un proveedor falla por token expirado
- **THEN** el sistema usa el refresh token para obtener uno nuevo y reintenta
- **AND** el nuevo token se persiste en Secrets Manager

#### Scenario: Las credenciales no se exponen

- **WHEN** se inspeccionan logs y la tabla de datos
- **THEN** no aparecen secretos en texto plano
- **AND** las credenciales solo residen en Secrets Manager

