## ADDED Requirements

### Requirement: Adapter de NetSuite sobre el connector framework

El conector de NetSuite SHALL implementar la interfaz de adapter y declarar las capacidades `inventario`
y, donde aplique, `pedidos`/facturas. La autenticación SHALL usar OAuth (Token-Based Authentication) con
credenciales en el vault. Es **deuda técnica diferida** (requiere licencia/cuenta NetSuite).

#### Scenario: Inventario sincronizado con NetSuite

- **WHEN** NetSuite actúa como fuente de verdad de inventario para ciertos artículos
- **THEN** el adapter trae los niveles de stock y los aplica al inventario unificado de forma idempotente
- **AND** los conflictos se resuelven según las reglas de fuente de verdad
