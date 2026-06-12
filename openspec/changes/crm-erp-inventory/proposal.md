## Why

Para operar como negocio real, los clientes deben sincronizarse con el **CRM** y el inventario/almacenes
con el **ERP/IMS**. Esto cierra el ciclo: clientes y pedidos del hub fluyen al CRM; el inventario puede
tener al ERP/IMS como fuente alterna o destino. Sprint 5 del roadmap. Se agrupan por ser, todos,
sincronización de entidades canónicas (cliente, inventario) con sistemas de gestión.

## What Changes

- **Adapters de CRM**: Salesforce (REST), HubSpot, Zoho CRM — sync bidireccional de **clientes/contactos**
  (canónico ↔ CRM) y, donde aplique, de pedidos como oportunidades/deals.
- **Adapters de ERP**: NetSuite (SuiteTalk/REST), Odoo (JSON-RPC) — sync de inventario/almacenes y, donde
  aplique, de pedidos/facturas.
- **Adapters de inventario multialmacén**: Cin7 / Skubana — niveles de stock por almacén hacia/desde el
  inventario unificado.
- Reglas de **fuente de verdad** configurables: por entidad se define qué sistema manda (p. ej. inventario
  desde el ERP, clientes desde el CRM), respetando idempotencia y mapeo de IDs del Sprint 1.

## Capabilities

### New Capabilities
- `salesforce-connector`: sync de clientes/oportunidades con Salesforce.
- `hubspot-connector`: sync de contactos/deals con HubSpot.
- `zoho-crm-connector`: sync de contactos/deals con Zoho CRM.
- `netsuite-connector`: sync de inventario/pedidos con NetSuite.
- `odoo-connector`: sync de inventario/pedidos con Odoo (JSON-RPC).
- `inventory-ims-connector`: sync de inventario multialmacén con Cin7/Skubana.
- `source-of-truth-rules`: configuración de qué sistema es fuente de verdad por entidad.

### Modified Capabilities
<!-- Puede refinar unified-inventory (Sprint 1) si el ERP/IMS pasa a ser fuente de verdad de stock. -->

## Impact

- **Backend**: `backend/integrations/{salesforce,hubspot,zoho,netsuite,odoo,inventory_ims}/`; lógica de
  resolución de fuente de verdad por entidad.
- **Datos**: extensión del mapeo de IDs y del estado de sync para entidades CRM/ERP.
- **Infra**: secretos OAuth por sistema; jobs de sync programados y por evento.
- **Tests**: HubSpot/Zoho/Odoo tienen ediciones/sandbox gratuitos; **Salesforce y NetSuite requieren
  cuenta/Developer Edition con límites**; Cin7/Skubana requieren cuenta.
- **Docs**: sección por conector; matriz de fuente de verdad.
- **Dependencia**: requiere `integration-platform-core` (Sprint 1).
