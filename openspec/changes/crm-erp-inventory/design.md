## Context

Sprint 5: sincronización de **clientes** (CRM) e **inventario/pedidos** (ERP/IMS) sobre el núcleo del
Sprint 1. A diferencia de los canales de venta (donde el canónico publica), aquí la **fuente de verdad
puede invertirse** (el ERP/IMS manda en inventario; el CRM en clientes). Por eso se introduce un
mecanismo explícito de reglas de fuente de verdad y dirección de sync.

## Goals / Non-Goals

**Goals:**
- Adapters de CRM (Salesforce, HubSpot, Zoho), ERP (NetSuite, Odoo) e IMS (Cin7/Skubana).
- Reglas configurables de fuente de verdad y dirección de sync por entidad.
- Sync idempotente de clientes y de inventario multialmacén con el inventario unificado.

**Non-Goals:**
- Contabilidad/facturación completa del ERP; alcance: inventario y, donde aplique, pedidos.
- Automatizaciones de marketing del CRM; alcance: sync de clientes/contactos (+ deals donde aplique).

## Decisions

### Decisión 1: Reglas de fuente de verdad por entidad
Configuración declarativa: por entidad (inventario/clientes/pedidos) se define el sistema fuente. El motor
del Sprint 1 respeta la regla; los subordinados no sobrescriben la fuente. Resuelve el riesgo de bucles de
sync y sobrescritura. Alternativa (último-en-escribir-gana) descartada por inconsistencias.

### Decisión 2: Dirección de sync declarada por conector
Cada adapter declara, por entidad, si soporta entrante/saliente/bidireccional. Combinado con la fuente de
verdad, evita escrituras no deseadas y respeta capacidades reales de cada API.

### Decisión 3: Agrupación por patrón, no por proveedor
CRM (cliente/contacto), ERP (inventario/pedidos), IMS (inventario multialmacén) comparten lógica; cada
adapter solo aporta auth y mapeo de campos. Reduce duplicación.

### Decisión 4: Deuda técnica diferida
Salesforce y NetSuite requieren cuenta/licencia → specced, implementación diferida (política tier 0).
HubSpot, Zoho y Odoo son ejecutables (free/community). Cin7/Skubana requieren cuenta del proveedor.

## Risks / Trade-offs

- **Bucles de sincronización** → reglas de fuente de verdad + idempotencia + marca de origen del cambio.
- **Conflictos de datos** → resolución determinista por fuente; registro en observabilidad.
- **Mapeo de campos dispares (CRM/ERP)** → mapeadores por adapter, probados con casos reales.
- **Acceso a Salesforce/NetSuite** → diferir como deuda técnica; no bloquea HubSpot/Zoho/Odoo/IMS.

## Migration Plan

1. Reglas de fuente de verdad y dirección de sync (base transversal).
2. CRM ejecutables: HubSpot, Zoho (sync de clientes; deals donde aplique).
3. ERP/IMS ejecutables: Odoo (JSON-RPC), Cin7/Skubana (inventario multialmacén).
4. Diferidos: Salesforce, NetSuite (codificados; verificación al tener acceso).

## Open Questions

- ¿Multialmacén: cómo agrega el inventario unificado el stock por almacén para "disponible para venta"?
- ¿Pedidos hacia el CRM como Deals/Oportunidades en qué casos aporta valor vs ruido?
