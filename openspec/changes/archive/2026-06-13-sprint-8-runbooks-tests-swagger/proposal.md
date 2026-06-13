## Why

Los Sprints 0–7 dejaron a MetalShop como un hub de comercio multicanal funcional: API serverless,
núcleo de integración, conectores de canal/marketplace/social/CRM/ERP/POS y panel de administración. Pero
la plataforma carece de tres **entregables transversales** que la hacen operable y mantenible por personas
distintas a quien la construyó:

- No hay **runbooks operativos** por tipo de usuario: un visitante, un cliente, un administrador o un
  operador/devops no tienen un procedimiento documentado, verificable y con troubleshooting para sus
  tareas. La operación vive en la cabeza del equipo.
- La **cobertura de pruebas unitarias** de servicios, repositorios, conectores, pricing y seguridad es
  desigual y no hay una convención clara ni un objetivo de cobertura medible.
- La **documentación Swagger/OpenAPI** existe solo de forma implícita (FastAPI genera el esquema), pero no
  está enriquecida (summaries, descriptions, tags, response models, ejemplos) ni publicada, y los
  conectores no-HTTP no tienen sus contratos documentados.

El Sprint 8 cierra esa deuda transversal: runbooks por tipo de usuario, una suite de pruebas unitarias con
objetivo de cobertura y convención, y documentación OpenAPI/Swagger completa de todos los servicios. Es la
capa que hace la plataforma **operable, verificable y auto-documentada**.

## What Changes

- **Runbooks por tipo de usuario** (`user-runbooks`): un runbook operativo por cada tipo de usuario
  (visitante, cliente, administrador, operador/devops), cada uno con objetivo, precondiciones, pasos,
  verificación y troubleshooting. Viven en `docs/runbooks/` como fuente canónica.
- **Suite de pruebas unitarias** (`unit-test-suite`): cobertura de pruebas unitarias de todos los servicios
  (repositorios, services, integraciones/conectores, pricing, seguridad), con un **objetivo de cobertura**
  medible y una **convención** clara (pytest + moto, aislamiento, naming), distinguiendo pruebas unitarias
  de pruebas de integración.
- **Documentación OpenAPI/Swagger** (`api-swagger`): exponer `/docs` (Swagger UI) y `/openapi.json`,
  enriquecer summaries/descriptions/tags/response models de cada router (auth, store/config, catalog, cart,
  orders, admin) y publicar el esquema. Para conectores/integraciones que no son HTTP, documentar sus
  contratos (capacidades, dirección de sync, payloads canónicos).
- **Regla SDD transversal**: a partir de este sprint, todo cambio OpenSpec que afecte el comportamiento de
  un tipo de usuario DEBE además actualizar su runbook, incluir pruebas unitarias de la lógica nueva y
  mantener al día la documentación Swagger/OpenAPI de los endpoints afectados (se formaliza en
  `docs/base-standards.md` §9 y en la regla de pasos obligatorios de tasks).

## Capabilities

### New Capabilities

- `user-runbooks`: un runbook operativo por tipo de usuario (visitante, cliente, administrador,
  operador/devops), cada uno con objetivo, precondiciones, pasos, verificación y troubleshooting.
- `unit-test-suite`: cobertura de pruebas unitarias de repositorios, services, integraciones/conectores,
  pricing y seguridad, con objetivo de cobertura medible y convención pytest + moto, distinguiendo
  unitarias de integración.
- `api-swagger`: documentación OpenAPI/Swagger de todos los servicios HTTP (auth, config, catalog, cart,
  orders, admin) con `/docs` y `/openapi.json` enriquecidos y publicados, y contratos documentados de los
  conectores no-HTTP.

### Modified Capabilities

<!-- No modifica specs vigentes en openspec/specs/. Este cambio es transversal y documental: consume el
     comportamiento de todas las capabilities de Sprints previos (serverless-api, store-configuration,
     dynamodb-persistence del Sprint 0; connector-framework, sync-engine, unified-orders del Sprint 1;
     conectores de los Sprints 2–6; panel-admin del Sprint 7) para documentarlas y probarlas, sin cambiar
     su contrato. El enriquecimiento de OpenAPI no cambia rutas ni shapes de respuesta. -->

## Impact

- **Dependencias**: requiere los Sprints 0–7 implementados (API serverless con routers auth/config/catalog/
  cart/orders, núcleo de integración, conectores y panel admin). El alcance es documental y de pruebas; no
  cambia contratos de endpoints ni el shape de las respuestas.
- **Documentación**: nuevo directorio `docs/runbooks/` con un runbook por tipo de usuario
  (`visitante.md`, `cliente.md`, `administrador.md`, `operador-devops.md`) y un índice
  `docs/runbooks/README.md`; nueva sección `docs/base-standards.md §9`; convención de pruebas en
  `docs/backend-standards.md`; contratos de conectores no-HTTP en `docs/integrations-standards.md`.
- **Backend (OpenAPI)**: enriquecer cada router en `backend/routers/*` con `summary`, `description`,
  `tags`, `response_model` y `responses` de error; configurar `FastAPI(...)` en `backend/app.py` con
  metadatos (título, versión, descripción, `openapi_tags`, servidores) y exponer `/docs` y
  `/openapi.json`. Sin cambios de rutas ni de lógica de negocio.
- **Tests**: nueva/ampliada suite unitaria en `tests/unit/` cubriendo repositorios (`backend/repositories/`),
  services (`backend/cart_service.py`, `backend/services/`), integraciones (`backend/integrations/` y sus
  conectores), `backend/pricing.py` y `backend/security.py`, con moto para AWS y objetivo de cobertura.
- **Reglas SDD**: `docs/base-standards.md` (nueva §9), `.claude/rules/openspec-tasks-mandatory-steps.md` y
  `.gemini/rules/openspec-tasks-mandatory-steps.md` (tres pasos obligatorios añadidos al final).
- **Seguridad**: la Swagger UI y `/openapi.json` no deben exponer secretos ni ejemplos con credenciales
  reales; en producción se evalúa proteger `/docs` o servirlo solo en entornos no productivos.
