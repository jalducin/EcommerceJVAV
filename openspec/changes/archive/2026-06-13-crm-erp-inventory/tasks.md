## 0. Preparación (OBLIGATORIO)

- [ ] 0.1 Crear y cambiar a la feature branch `feature/crm-erp-inventory` (Step 0 — SIEMPRE primero)
- [ ] 0.2 Leer `openspec/config.yaml`, `docs/integrations-standards.md` y la regla de pasos obligatorios
- [ ] 0.3 Confirmar Sprint 1 implementado; crear cuentas free/sandbox (HubSpot, Zoho, Odoo local) y credenciales en el vault

## 1. Reglas de fuente de verdad y dirección de sync (base transversal)

- [ ] 1.1 Modelar la configuración de fuente de verdad por entidad (inventario/clientes/pedidos)
- [ ] 1.2 Declaración de dirección de sync por conector/entidad (entrante/saliente/bidireccional)
- [ ] 1.3 Integrar la resolución de conflictos con el motor del Sprint 1 (registro en observabilidad)

## 2. CRM ejecutables (HubSpot, Zoho)

- [ ] 2.1 `backend/integrations/hubspot/` — OAuth/Private App, sync de Contactos (+ Deals donde aplique), idempotente
- [ ] 2.2 `backend/integrations/zoho/` — OAuth, sync de Contactos/Leads (+ Deals donde aplique), idempotente

## 3. ERP/IMS ejecutables (Odoo, Cin7/Skubana)

- [ ] 3.1 `backend/integrations/odoo/` — JSON-RPC, sync de inventario (+ pedidos donde aplique)
- [ ] 3.2 `backend/integrations/inventory_ims/` — Cin7/Skubana, inventario multialmacén ↔ unificado

## 4. CRM/ERP diferidos (DEUDA TÉCNICA — implementación diferida)

- [ ] 4.1 `backend/integrations/salesforce/` — estructura + OAuth (verificación diferida por falta de org)
- [ ] 4.2 `backend/integrations/netsuite/` — estructura + TBA OAuth (verificación diferida por falta de cuenta)
- [ ] 4.3 DIFERIDO: dejar sin marcar como completos hasta tener acceso; registrar en el roadmap

## 5. Revisar y actualizar pruebas (OBLIGATORIO)

- [ ] 5.1 Pruebas de reglas de fuente de verdad (ERP manda inventario; CRM manda clientes; conflicto resuelto)
- [ ] 5.2 Pruebas de sync idempotente de clientes (HubSpot/Zoho) y de inventario (Odoo/IMS) contra sandbox/respuestas grabadas
- [ ] 5.3 Prueba anti-bucle: un cambio originado por sync no dispara un re-sync infinito

## 6. Ejecutar pruebas y verificar estado (OBLIGATORIO — EL AGENTE EJECUTA)

- [ ] 6.1 `ruff check .` sin errores y `pytest` en verde
- [ ] 6.2 Reporte en `specs/crm-erp-inventory/reports/AAAA-MM-DD-step-6-pruebas-y-verificacion.md`

## 7. Verificación manual E2E (OBLIGATORIO — EL AGENTE EJECUTA)

- [ ] 7.1 Crear un cliente canónico y verificar el Contacto en HubSpot y Zoho (idempotente)
- [ ] 7.2 Cambiar stock en Odoo/IMS (fuente de verdad) y verificar que el inventario unificado lo refleja sin sobrescribir la fuente
- [ ] 7.3 Restaurar estado; documentar en el reporte; anotar Salesforce/NetSuite como diferidos

## 8. Actualizar documentación (OBLIGATORIO)

- [ ] 8.1 Documentar conectores y la matriz de fuente de verdad en `docs/integrations-standards.md`
- [ ] 8.2 Actualizar `docs/roadmap-plataforma-multicanal.md` (Sprint 5; Salesforce/NetSuite como deuda técnica)
- [ ] 8.3 Verificar consistencia documental: 0 referencias rotas
