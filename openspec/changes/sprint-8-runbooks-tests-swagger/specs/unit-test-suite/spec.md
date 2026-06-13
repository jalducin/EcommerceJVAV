## ADDED Requirements

### Requirement: Convención de pruebas unitarias

El proyecto SHALL definir una convención única de pruebas unitarias documentada en
`docs/backend-standards.md`: las pruebas unitarias viven en `tests/unit/` con un archivo `test_<modulo>.py`
por módulo, se nombran `test_<comportamiento>_<condicion>`, usan pytest y aíslan dependencias externas
(DynamoDB y demás servicios AWS con moto; clientes HTTP de conectores con mocks). Las pruebas de
integración viven en `tests/integration/` y NO cuentan para el objetivo de cobertura unitaria.

#### Scenario: Una prueba unitaria está aislada

- **WHEN** se ejecuta una prueba en `tests/unit/`
- **THEN** no realiza llamadas reales a AWS ni a APIs externas (usa moto y mocks)
- **AND** sigue el naming `test_<comportamiento>_<condicion>` en un archivo `test_<modulo>.py`

#### Scenario: Distinción entre unitaria e integración

- **WHEN** una prueba ejerce el flujo real entre capas o un sandbox de proveedor externo
- **THEN** se ubica en `tests/integration/` y no en `tests/unit/`
- **AND** no se contabiliza para el objetivo de cobertura unitaria

### Requirement: Objetivo de cobertura medible

La suite unitaria MUST alcanzar un objetivo de cobertura de ≥85% de líneas del paquete `backend/`
(excluyendo el arranque `app.py` y handlers triviales), medido con `pytest --cov`, con un mínimo por paquete
que garantice que los módulos críticos (`security.py`, `pricing.py`) queden cubiertos.

#### Scenario: La suite cumple el objetivo de cobertura

- **WHEN** se ejecuta `pytest --cov=backend` con la suite unitaria
- **THEN** la cobertura global de `backend/` es ≥85% de líneas según el reporte
- **AND** los módulos críticos `security.py` y `pricing.py` no quedan por debajo del mínimo por paquete

#### Scenario: La cobertura es reproducible

- **WHEN** el agente ejecuta la suite unitaria en CI o en local
- **THEN** el reporte de cobertura se genera de forma determinista (mismo conjunto de pruebas, mismo umbral)
- **AND** un descenso por debajo del umbral hace fallar la verificación

### Requirement: Cobertura de repositorios y servicios

Las pruebas unitarias SHALL cubrir los repositorios (`backend/repositories/`) y los servicios de dominio
(`backend/cart_service.py` y `backend/services/`), ejercitando caminos de éxito y de error con DynamoDB
mockeado vía moto.

#### Scenario: Repositorios y servicios cubren éxito y error

- **WHEN** se ejecutan las pruebas unitarias de repositorios y servicios
- **THEN** cubren operaciones de lectura/escritura exitosas y casos de error (no encontrado, conflicto)
- **AND** usan moto para DynamoDB sin tocar infraestructura real

### Requirement: Cobertura de integraciones y conectores

Las pruebas unitarias SHALL cubrir el framework de integración (`backend/integrations/connector.py`,
`canonical.py`, `mapping.py`) y cada conector de `backend/integrations/connectors/`, verificando capacidades
declaradas, dirección de sync y traducción entre el modelo externo y el canónico, con los clientes externos
mockeados.

#### Scenario: Un conector traduce al modelo canónico

- **WHEN** se ejecuta la prueba unitaria de un conector con una respuesta externa mockeada
- **THEN** verifica que el adapter traduce el payload externo al modelo canónico esperado
- **AND** valida las capacidades declaradas y la dirección de sync del conector

#### Scenario: Conector diferido por deuda técnica

- **WHEN** un conector está marcado como deferred por requerir cuenta pagada
- **THEN** su prueba unitaria ejerce la traducción contra respuestas grabadas/mock sin acceso real
- **AND** no se marca como prueba de integración bloqueada por falta de credenciales

### Requirement: Cobertura de pricing y seguridad

Las pruebas unitarias MUST cubrir `backend/pricing.py` (cálculo de totales según la configuración de tienda)
y `backend/security.py` (hash/verificación de contraseñas y emisión/decodificación de tokens), por ser
lógica crítica de negocio y de seguridad.

#### Scenario: Pricing calcula totales correctos

- **WHEN** se ejecuta la prueba unitaria de `compute_totals` con un subtotal y una configuración de tienda
- **THEN** el total refleja impuestos y reglas de la configuración
- **AND** se cubren casos límite (subtotal cero, configuración sin impuestos)

#### Scenario: Security tokens y contraseñas

- **WHEN** se ejecutan las pruebas unitarias de `security.py`
- **THEN** verifican que una contraseña se hashea y verifica correctamente y que un token inválido/expirado se rechaza al decodificar
- **AND** un access token válido se decodifica con su tipo y claims esperados
