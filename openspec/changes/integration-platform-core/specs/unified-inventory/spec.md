## ADDED Requirements

### Requirement: Inventario como fuente única de verdad

El sistema SHALL mantener el inventario canónico como **fuente única de verdad** del stock disponible por
variante/ubicación. Toda venta (cualquier canal o POS) SHALL descontar de este inventario, y toda
publicación de stock a un canal SHALL derivarse de él.

#### Scenario: Venta en un canal actualiza el stock canónico

- **WHEN** se confirma una venta en cualquier canal
- **THEN** el inventario canónico de esa variante se descuenta
- **AND** el nuevo nivel queda disponible para propagarse a los demás canales

### Requirement: Prevención de sobreventa entre canales

La actualización de inventario SHALL impedir vender por debajo de cero. Cuando dos canales intenten vender
la última unidad casi simultáneamente, el sistema SHALL garantizar que solo una venta tenga éxito,
mediante actualización condicional/atómica del nivel de inventario.

#### Scenario: Carrera por la última unidad

- **WHEN** dos canales intentan vender la última unidad de una variante a la vez
- **THEN** solo una de las dos ventas descuenta el stock con éxito
- **AND** la otra falla por condición de stock insuficiente, sin dejar inventario negativo

### Requirement: Propagación de cambios de stock a los canales

Un cambio en el inventario canónico SHALL disparar la propagación del nuevo nivel a los canales conectados
que soporten inventario, a través del motor de sincronización (asíncrono, idempotente, con rate limiting).

#### Scenario: Cambio de stock se propaga a los canales activos

- **WHEN** cambia el nivel de inventario de una variante publicada en dos canales
- **THEN** el motor encola la actualización de stock para ambos canales
- **AND** cada canal recibe el nuevo nivel respetando su rate limit
