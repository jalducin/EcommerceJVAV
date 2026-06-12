## ADDED Requirements

### Requirement: Adapter de Google Merchant Center sobre el connector framework

El conector de Google Merchant SHALL implementar la interfaz de adapter y declarar la capacidad `catalogo`
(feed de productos para Google Shopping vía Content API for Shopping). La autenticación SHALL usar una
cuenta de servicio / OAuth de Google con credenciales en el vault. Es principalmente un canal de **feed**
(sin pedidos en el alcance base).

#### Scenario: Productos canónicos publicados en Google Merchant

- **WHEN** se sincroniza el catálogo hacia Google Merchant Center
- **THEN** el adapter inserta/actualiza los productos vía Content API resolviendo el mapeo de IDs
- **AND** los cambios de precio/disponibilidad se propagan por el motor de sincronización

#### Scenario: Producto inválido reportado, no rompe el lote

- **WHEN** un producto es rechazado por Google por datos faltantes (p. ej. GTIN)
- **THEN** el error se registra para ese producto en la observabilidad
- **AND** el resto del feed se publica sin abortar todo el trabajo
