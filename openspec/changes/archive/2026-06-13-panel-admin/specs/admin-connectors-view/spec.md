## ADDED Requirements

### Requirement: Vista de estado de sincronización por conector

La vista de conectores SHALL mostrar, por cada conector del registro, su estado de sincronización (último sync correcto, trabajos en cola, conteo en DLQ) tomado de la observabilidad del Sprint 1, y SHALL distinguir visualmente los conectores marcados como `deferred` (deuda técnica, sin verificación en vivo).

#### Scenario: Conector con fallos en DLQ

- **WHEN** un conector acumula mensajes en la DLQ
- **THEN** la vista muestra su conteo en DLQ y el último sync con indicador de fallo
- **AND** permite identificar que requiere atención

#### Scenario: Conector marcado como deferred

- **WHEN** un conector está marcado como `deferred` (deuda técnica)
- **THEN** la vista lo señala como diferido y no exige métricas de sync en vivo
- **AND** lo separa de los conectores operativos

#### Scenario: Sin conectores habilitados

- **WHEN** el registro de conectores está vacío
- **THEN** la vista muestra un estado vacío informativo
- **AND** no produce error

### Requirement: Habilitar y deshabilitar conectores

La vista de conectores SHALL permitir habilitar y deshabilitar un conector (registrarlo o quitarlo del registro), reflejando de inmediato el cambio de estado, mediante un endpoint admin protegido con `require_admin`.

#### Scenario: Deshabilitar un conector activo

- **WHEN** el admin deshabilita un conector habilitado
- **THEN** el conector se quita del registro y deja de aparecer como operativo
- **AND** sus métricas de sync ya no se muestran como activas

#### Scenario: Habilitar un conector disponible

- **WHEN** el admin habilita un conector disponible
- **THEN** el conector queda registrado con sus capacidades declaradas
- **AND** la vista lo muestra como operativo
