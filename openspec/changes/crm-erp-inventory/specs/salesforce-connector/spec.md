## ADDED Requirements

### Requirement: Adapter de Salesforce sobre el connector framework

El conector de Salesforce SHALL implementar la interfaz de adapter y declarar la capacidad `clientes`
(sync de Cuentas/Contactos) y, donde aplique, `pedidos` como Oportunidades. La autenticación SHALL usar
OAuth 2.0 con tokens en el vault. Es **deuda técnica diferida** (requiere org; Developer Edition limitada).

#### Scenario: Cliente canónico sincronizado como Contacto

- **WHEN** se crea o actualiza un cliente canónico marcado para Salesforce
- **THEN** el adapter crea/actualiza el Contacto vía REST API resolviendo el mapeo de IDs
- **AND** la operación es idempotente (no duplica el Contacto)
