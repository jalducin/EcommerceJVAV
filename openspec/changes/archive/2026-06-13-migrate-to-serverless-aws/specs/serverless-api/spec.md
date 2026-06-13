## ADDED Requirements

### Requirement: API ejecutada como Lambda detrás de API Gateway

La API FastAPI SHALL ejecutarse como una única función AWS Lambda ("Lambdalith") adaptada con Mangum y
expuesta a través de API Gateway (HTTP API). La Lambda SHALL atender únicamente las rutas `/api/*`; el
contenido estático NO se sirve desde la Lambda.

#### Scenario: Petición HTTP enrutada a la Lambda

- **WHEN** un cliente hace `GET /api/health` contra la URL de API Gateway
- **THEN** API Gateway invoca la Lambda, Mangum traduce el evento a ASGI
- **AND** la respuesta es `200` con `{"status": "ok"}`

#### Scenario: Ruta de API inexistente

- **WHEN** un cliente hace `GET /api/no-existe`
- **THEN** la respuesta es `404` con cuerpo JSON de error de FastAPI

### Requirement: Ejecución sin estado entre invocaciones

La Lambda SHALL ser stateless: no SHALL depender de estado en memoria que persista entre invocaciones
(sesiones, contadores, archivos temporales) para su correcto funcionamiento. Todo estado compartido
SHALL residir en DynamoDB u otro servicio gestionado.

#### Scenario: Dos peticiones servidas por invocaciones distintas

- **WHEN** dos peticiones autenticadas del mismo usuario las atienden contenedores Lambda diferentes
- **THEN** ambas se resuelven correctamente leyendo el estado desde DynamoDB
- **AND** ningún resultado depende de datos guardados en memoria por una invocación previa

### Requirement: Arranque en frío aceptable

El inicio en frío de la Lambda SHALL completarse en un tiempo aceptable para aprendizaje (objetivo
< 3 s con la memoria configurada). Las dependencias pesadas de CPU (hashing bcrypt) SHALL considerarse al
dimensionar la memoria de la Lambda.

#### Scenario: Primera invocación tras periodo de inactividad

- **WHEN** llega una petición tras un periodo sin invocaciones (cold start)
- **THEN** la Lambda inicializa y responde correctamente
- **AND** el tiempo total de respuesta se registra para evaluar el dimensionamiento de memoria
