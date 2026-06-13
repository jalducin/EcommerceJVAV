---
description: Reglas y guías de desarrollo del proyecto, aplicables a todos los agentes de IA (Claude, Gemini, etc.).
alwaysApply: true
---

# Estándares base

> Plantilla SDD (Spec-Driven Development). Este documento es genérico y sirve para cualquier
> stack (Python, PHP, React, n8n, etc.). Ajusta lo que sea específico de tu proyecto al instanciarla.

## 1. Principios fundamentales

- **Tareas pequeñas, una a la vez**: avanzar en pasos cortos. No saltar más de un paso a la vez.
- **Desarrollo guiado por pruebas (TDD)**: cuando aplique, empezar por una prueba que falle antes de implementar.
- **Seguridad de tipos / contratos claros**: tipar el código cuando el lenguaje lo permita; definir contratos explícitos.
- **Nombres claros**: nombres descriptivos para variables, funciones y artefactos.
- **Cambios incrementales**: preferir cambios pequeños y enfocados sobre modificaciones grandes y complejas.
- **Cuestionar supuestos**: validar suposiciones e inferencias antes de implementar.
- **Detección de patrones**: identificar y señalar código repetido.

## 2. Estándar de idioma

- **Documentación y comentarios: español.** README, guías, comentarios de código, mensajes de commit,
  descripciones de pruebas y artefactos OpenSpec se redactan en español.
- **Identificadores de código** (variables, funciones, clases): seguir la convención idiomática del
  lenguaje del proyecto (habitualmente inglés). La coherencia dentro del proyecto manda.
- Cada proyecto puede ajustar esta regla en su propio `docs/*-standards.md` si lo necesita.

## 3. Estándares específicos

Para guías detalladas por área, cada proyecto agrega sus documentos en `docs/`:

- `docs/<area>-standards.md` — por ejemplo `backend-standards.md`, `frontend-standards.md`,
  `sql-standards.md`, `n8n-standards.md`, según el stack del proyecto.
- `docs/documentation-standards.md` — estructura, formato y mantenimiento de la documentación.

Crea solo los que apliquen a tu proyecto y enlázalos desde `openspec/config.yaml`.

## 4. Skills del proyecto

- Las skills viven en `ai-specs/skills`.
- Cuando una petición coincide con una skill, cargar y seguir su `SKILL.md` automáticamente antes de continuar.
- Cargar también los archivos referenciados por la skill (por ejemplo `references/*.md`) cuando los requiera.

## 5. Requisito de modelo para planificación

Los flujos de planificación deben ejecutarse con un modelo de razonamiento alto (Opus high reasoning).

Aplica a:
- `enrich-us`
- `openspec-ff-change`
- `openspec-continue-change`

Antes de iniciar cualquiera de estos flujos, verificar que la sesión usa un modelo de razonamiento alto.
Si no, **autocorregir** ajustando el modelo en la configuración del agente (`.claude/settings.json` para Claude),
y continuar — no detenerse a preguntar. Volver al modelo estándar para el resto de pasos.

## 6. Integridad de referencias y portabilidad multi-agente

- **Fuente canónica**: mantener los artefactos reutilizables en `ai-specs` como fuente única. Las rutas
  específicas por agente (`.claude`, `.gemini`) referencian esa fuente (symlink donde el SO lo permita;
  copia real en Windows).
- **Seguridad al actualizar**: al renombrar o mover un archivo, verificar y actualizar todas las
  referencias/symlinks que lo apunten antes de dar el cambio por terminado.
- **Enlazado de artefactos nuevos**: al crear un artefacto que requiere exposición multi-agente (agentes o
  skills en `ai-specs`), crear las referencias correspondientes desde las rutas de cada agente.
- **Revisión de personalización externa**: si se introduce personalización fuera de `ai-specs`, evaluar
  moverla a `ai-specs` y referenciarla desde su ubicación original.
- **Compuerta de cierre**: un cambio está incompleto si deja referencias rotas, destinos obsoletos o
  artefactos canónicos duplicados entre carpetas de agentes.

## 7. Actualización obligatoria de artefactos OpenSpec en cambios post-apply

Cuando aparece un nuevo arreglo/cambio después de `opsx:apply` (o `/apply`) y antes de `opsx:archive`
(o `/archive`), debe tratarse como una actualización del spec primero, no como un "arréglalo rápido".
Es el principio central de OpenSpec: la documentación es la fuente de verdad.

Orden requerido:

1. Actualizar los artefactos del cambio OpenSpec afectados (escenarios, requisitos/specs y `tasks.md`).
   No agregar tareas como "bugfixes" sueltos, sino como parte del diseño en la sección correspondiente.
2. Si hace falta regenerar artefactos, ejecutar el paso OpenSpec correspondiente (`opsx:continue`, `opsx:ff`
   o equivalente) antes de codificar.
3. Implementar código solo después de que los artefactos reflejen la nueva petición.
4. Re-ejecutar la verificación contra los artefactos actualizados antes de archivar.

No aplicar arreglos directos solo en código dentro de esa ventana sin actualizar los artefactos OpenSpec.

## 8. Autonomía: no pedir autorización para lo básico

Extiende el principio de §5 ("autocorregir y continuar — no detenerse a preguntar"). El agente DEBE
**actuar de forma autónoma en operaciones básicas, reversibles o de bajo riesgo**, y reportar lo hecho,
**sin pedir confirmación**. Pausar a preguntar solo para decisiones genuinamente consecuentes.

### Proceder sin preguntar (verde)

- Leer/buscar/explorar el código y la documentación.
- Correr pruebas, lint, formato, type-check; ejecutar el proyecto en local; verificación manual.
- Crear/cambiar de feature branch; commits; instalar dependencias del proyecto; generar/editar artefactos
  OpenSpec; aplicar tareas de un cambio; mover/renombrar/refactorizar código propio del proyecto.
- Operaciones idempotentes o fácilmente reversibles (incluye recursos efímteros de prueba que se limpian,
  p. ej. una tabla temporal que se elimina al terminar).
- Elegir entre alternativas equivalentes de implementación: tomar la mejor opción razonada y seguir.

### Confirmar antes (rojo)

Pedir autorización solo cuando la acción es **difícil de revertir, hacia afuera, o con costo/impacto real**:

- `git push`, abrir/mergear PRs a ramas protegidas, **force-push**, reescritura de historial publicado.
- **Despliegues a producción**, o creación de infraestructura cloud **persistente** con costo no trivial.
- Borrado/sobrescritura de datos del usuario, secretos, o recursos que el agente no creó.
- Acciones que gastan dinero, envían comunicaciones externas, o exponen datos a terceros.
- Cambios de alcance del producto/arquitectura no derivables del contexto (decisiones de negocio).

### Cómo reportar

Tras actuar, indicar en una línea qué se hizo y el resultado verificado. Si una decisión "verde" resultara
relevante, dejarla registrada (commit/artefacto), no preguntarla. Ante la duda entre verde y rojo, preferir
avanzar si es reversible; detenerse solo si el daño potencial es real e irreversible.

> Nota de harness (Claude Code): para reducir prompts de permisos en comandos seguros y rutinarios, el
> proyecto puede mantener un allowlist en `.claude/settings.json` (no versionado). Ver la skill
> `update-config` / `fewer-permission-prompts`.

## 9. Entregables transversales obligatorios

Todo cambio OpenSpec que **afecte el comportamiento de un tipo de usuario** (visitante, cliente,
administrador, operador/DevOps) DEBE entregar, además del código y en el mismo PR, tres entregables
transversales. Un cambio que afecte a un tipo de usuario está **incompleto** si omite cualquiera de ellos:

1. **Runbook del/los tipo(s) de usuario afectado(s).** Actualizar o crear el runbook operativo
   correspondiente en `docs/runbooks/` (uno por tipo de usuario, fuente canónica), con sus secciones
   **Objetivo, Precondiciones, Pasos, Verificación y Troubleshooting**. Si el cambio altera un flujo que
   un tipo de usuario ejecuta, su runbook debe reflejar el nuevo procedimiento.
2. **Pruebas unitarias de la lógica nueva/cambiada.** Incluir pruebas unitarias (en `tests/unit/`, según la
   convención de `docs/backend-standards.md`) que cubran la lógica nueva o modificada — repositorios,
   services, integraciones/conectores, pricing o seguridad — manteniendo el objetivo de cobertura del
   proyecto. Las pruebas de integración (`tests/integration/`) no sustituyen a las unitarias.
3. **Documentación Swagger/OpenAPI al día.** Mantener sincronizada la documentación OpenAPI de los
   endpoints afectados: `summary`, `description`, `tags`, `response_model` y respuestas de error de cada
   operación tocada, de modo que `/docs` y `/openapi.json` reflejen el contrato real. Para integraciones
   no-HTTP (conectores), actualizar su contrato en `docs/integrations-standards.md`.

Estos tres entregables se operacionalizan como **pasos obligatorios** en
`.claude/rules/openspec-tasks-mandatory-steps.md` (y su réplica `.gemini/rules/...`, ver §6), que el
`tasks.md` de cada cambio debe incluir.
