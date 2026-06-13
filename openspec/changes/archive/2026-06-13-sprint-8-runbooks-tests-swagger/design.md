## Context

Sprint 8 del roadmap. Es un sprint **transversal y documental**: no añade comportamiento de producto, sino
que cierra la deuda de operabilidad, verificabilidad y auto-documentación que dejaron los Sprints 0–7. Tres
capabilities independientes pero complementarias: runbooks por tipo de usuario, suite de pruebas unitarias y
documentación OpenAPI/Swagger. Además formaliza una regla SDD para que estos tres entregables sean
obligatorios en todo cambio futuro que afecte a un tipo de usuario.

Tipos de usuario del sistema (base para los runbooks):
- **Visitante**: navega y busca el catálogo sin sesión.
- **Cliente**: se registra/inicia sesión, gestiona carrito, hace checkout y consulta sus pedidos.
- **Administrador**: gestiona catálogo con variantes, pedidos, dashboard y conectores (panel admin del Sprint 7).
- **Operador/DevOps**: despliega con SAM, siembra datos, rota secretos del vault, hace teardown y lee
  logs/DLQ.

Servicios a documentar en OpenAPI (HTTP, hoy en `backend/`):
- `auth` (`/api/auth`: register, login, refresh, me).
- `config` (`/api/config`).
- `products` (`/api/products`: list, get, create, update, delete).
- `cart` (`/api/cart`: get, add item, update item, delete item, sync).
- `orders` (`/api/orders`: checkout, list, get).
- `health` (`/api/health`).
- `admin` (`/api/admin`: dashboard, orders, cambio de estado, conectores) — del Sprint 7.

Servicios no-HTTP a documentar como contratos (no aparecen en OpenAPI): conectores de
`backend/integrations/connectors/` y el framework (`connector.py`, `canonical.py`, `mapping.py`,
`channel_orders.py`, `inventory.py`, `vault.py`, `webhooks.py`, `ingest.py`).

## Goals / Non-Goals

**Goals:**
- Un runbook operativo por tipo de usuario, accionable y con troubleshooting.
- Suite de pruebas unitarias con objetivo de cobertura medible y convención clara (pytest + moto),
  distinguiendo unitarias de integración.
- OpenAPI/Swagger completo: `/docs` y `/openapi.json` enriquecidos y publicados; contratos de conectores
  no-HTTP documentados.
- Regla SDD que obligue runbook + pruebas unitarias + Swagger en cambios futuros que afecten a un tipo de usuario.

**Non-Goals:**
- No cambiar rutas, shapes de respuesta ni lógica de negocio de ningún endpoint (solo metadatos OpenAPI).
- No alcanzar 100% de cobertura artificial; el objetivo es cobertura significativa de la lógica de dominio.
- No construir un portal de documentación externo; `/docs` (Swagger UI) basta para v1.
- No automatizar la ejecución de runbooks (son procedimientos humanos; su verificación es manual).

## Decisions

### Decisión 1: Runbooks en `docs/runbooks/` por tipo de usuario, un archivo por tipo
Fuente canónica única en `docs/runbooks/{visitante,cliente,administrador,operador-devops}.md` + índice
`README.md`. Estructura fija por runbook: **Objetivo · Precondiciones · Pasos · Verificación ·
Troubleshooting**. Alternativa (un solo runbook gigante) descartada por difícil de mantener y de enrutar al
usuario correcto.

### Decisión 2: Suite unitaria en `tests/unit/` con moto, separada de integración
Las pruebas unitarias aíslan la lógica (repos con DynamoDB mockeado vía moto, services y conectores con
clientes HTTP/AWS mockeados, pricing y security puros). Las pruebas de integración (flujo real entre capas,
sandbox de proveedor) van en `tests/integration/` y no cuentan para el objetivo de cobertura unitaria.
Convención: un archivo `test_<modulo>.py` por módulo, naming `test_<comportamiento>_<condicion>`. Objetivo
de cobertura: ≥85% de líneas en `backend/` excluyendo `app.py`/arranque, medido con `pytest --cov`.

### Decisión 3: OpenAPI enriquecido en el código de los routers, no en un archivo aparte
FastAPI genera el esquema desde los decoradores; se enriquece **en el sitio** (`summary`, `description`,
`tags`, `response_model`, `responses`) y se centralizan los `openapi_tags` y metadatos en `backend/app.py`.
`/docs` y `/openapi.json` quedan expuestos. Alternativa (mantener un YAML OpenAPI a mano) descartada: se
desincroniza del código y contradice la fuente única de verdad.

### Decisión 4: Conectores no-HTTP se documentan como contratos en `docs/integrations-standards.md`
Como no aparecen en OpenAPI, cada conector documenta su contrato: capacidades declaradas
(`Capability`), dirección de sync (`SyncDirection`), payloads canónicos de entrada/salida
(`canonical.py`) y mapeo de IDs externos↔canónicos. Así "todos los servicios" quedan documentados, HTTP o no.

### Decisión 5: La regla SDD se formaliza en dos lugares y se replica multi-agente
La obligación transversal se enuncia en `docs/base-standards.md §9` (principio) y se operacionaliza como
tres pasos obligatorios en la regla de tasks (`.claude/rules/...` y su réplica `.gemini/rules/...`, por la
política de portabilidad multi-agente de base-standards §6). Numeración coherente: los nuevos pasos van al
final de la lista existente (Step N+4, N+5, N+6) sin romper la secuencia previa.

## Risks / Trade-offs

- **Swagger expone secretos por accidente** → ejemplos sin credenciales reales; en producción evaluar
  proteger `/docs`/`/openapi.json` o servirlo solo en entornos no productivos (decisión de seguridad).
- **Objetivo de cobertura demasiado rígido** → se fija ≥85% de líneas de dominio y se documenta qué se
  excluye (arranque, handlers triviales) para no incentivar pruebas vacías.
- **Runbooks se desactualizan** → mitigado por la regla SDD §9: todo cambio que afecte a un tipo de usuario
  actualiza su runbook en el mismo PR.
- **moto no cubre toda la API de AWS** → para lo no soportado por moto, marcar como prueba de integración
  (sandbox real) y no como unitaria; documentarlo en la convención.

## Migration Plan

1. Documentación: crear `docs/runbooks/` con los cuatro runbooks + índice; añadir `docs/base-standards.md §9`;
   añadir convención de pruebas en `docs/backend-standards.md`; documentar contratos de conectores en
   `docs/integrations-standards.md`.
2. Reglas SDD: añadir los tres pasos obligatorios a `.claude/rules/openspec-tasks-mandatory-steps.md` y
   replicar en `.gemini/rules/openspec-tasks-mandatory-steps.md`.
3. Backend OpenAPI: enriquecer routers y `app.py`; exponer y verificar `/docs` y `/openapi.json`.
4. Tests: crear `tests/unit/` por módulo, configurar `pytest --cov`, alcanzar el objetivo de cobertura.
5. Verificación: ejecutar los runbooks manualmente (E2E por tipo de usuario), correr la suite con cobertura
   y validar el esquema OpenAPI.

## Open Questions

- ¿`/docs` debe quedar deshabilitado en producción o protegido tras `require_admin`? (Propuesta: deshabilitar
  en producción salvo flag explícito; siempre disponible en dev/staging.)
- ¿El objetivo de cobertura se mide global o por paquete? (Propuesta: global ≥85% con mínimo por paquete
  para evitar huecos en módulos críticos como `security.py` y `pricing.py`.)
