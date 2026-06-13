# transactional-email-ses Specification

## Purpose
TBD - created by archiving change migrate-to-serverless-aws. Update Purpose after archive.
## Requirements
### Requirement: Confirmación de pedido por Amazon SES

El correo de confirmación de pedido SHALL enviarse mediante Amazon SES (vía SDK o SMTP de SES), no por un
servidor SMTP genérico. El envío SHALL ejecutarse tras crear el pedido correctamente y NO SHALL bloquear
ni revertir el pedido si el correo falla (el fallo de email se registra, el pedido permanece).

#### Scenario: Pedido creado dispara correo SES

- **WHEN** un checkout crea un pedido correctamente
- **THEN** se envía un correo de confirmación vía SES con el número de pedido y el detalle
- **AND** el correo usa la plantilla con la marca de la configuración de tienda

#### Scenario: Fallo de envío no revierte el pedido

- **WHEN** el envío por SES falla (p. ej. cuota o dirección no verificada)
- **THEN** el pedido permanece creado y la API responde éxito del checkout
- **AND** el error de email queda registrado para diagnóstico

### Requirement: Identidad de remitente y modo sandbox documentados

La configuración SHALL usar una identidad de remitente verificada en SES. El comportamiento en
**sandbox** de SES (solo destinatarios verificados) SHALL estar documentado para el entorno de aprendizaje.

#### Scenario: Remitente verificado en sandbox

- **WHEN** se envía un correo en modo sandbox a un destinatario verificado
- **THEN** el correo se entrega correctamente
- **AND** la documentación indica cómo verificar identidades y salir de sandbox

