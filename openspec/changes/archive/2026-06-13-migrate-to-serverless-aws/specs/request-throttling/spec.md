## ADDED Requirements

### Requirement: Throttling de login en API Gateway

La protección contra abuso del endpoint de login SHALL implementarse con throttling a nivel de API
Gateway (rate y burst configurables por ruta), reemplazando a `slowapi` en memoria, que NO funciona entre
invocaciones Lambda aisladas. La dependencia `slowapi` SHALL eliminarse del backend.

#### Scenario: Exceso de intentos de login es limitado

- **WHEN** un cliente excede el rate configurado de `POST /api/auth/login`
- **THEN** API Gateway responde `429 Too Many Requests` sin invocar la Lambda
- **AND** las peticiones dentro del límite siguen funcionando

#### Scenario: slowapi removido

- **WHEN** se inspecciona el backend tras el cambio
- **THEN** no existe configuración de `slowapi` ni el módulo `limiter.py` en uso
- **AND** el throttling queda definido en la infraestructura (SAM/API Gateway)
