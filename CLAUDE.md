# CLAUDE.md — Instrucciones para Claude Code
## MetalShop · Ecommerce Python + FastAPI

---

## 📐 Metodología: Spec-Driven Development (OpenSpec)

Este proyecto trabaja bajo **SDD (Spec-Driven Development)** sobre OpenSpec. La especificación es la
fuente de verdad: todo cambio nuevo o mejora recorre artefactos antes de codificar.

Lee y aplica los estándares base del proyecto: @docs/base-standards.md

```
proposal  →  specs  →  design  →  tasks  →  (apply / implementación)  →  archive
   ¿por qué?   ¿qué?     ¿cómo?    ¿pasos?       código + verificación      cierre
```

- Comandos del flujo en Claude Code: `/opsx:new`, `/opsx:ff`, `/opsx:continue`, `/opsx:explore`,
  `/opsx:apply`, `/opsx:verify`, `/opsx:sync`, `/opsx:archive`. Ver `README.md` (sección Cómo contribuir).
- Contexto y reglas del proyecto: `openspec/config.yaml` y `openspec/project.md`.
- Estándares por área: `docs/base-standards.md`, `docs/documentation-standards.md`,
  `docs/backend-standards.md`, `docs/frontend-standards.md`.
- Pasos obligatorios de cada cambio: `.claude/rules/openspec-tasks-mandatory-steps.md`
  (rama → pruebas → verificación manual ejecutada por el agente → documentación).
- Para implementar, adopta el agente relevante de `ai-specs/agents/` (`backend-developer`, `frontend-developer`).

> Los archivos `SPEC.md`, `PLAN.md` y `TASKS.md` son la **línea base v1** (historial del producto ya
> implementado). El trabajo nuevo —mejoras y construcción faltante (backlog v2)— se gestiona como
> cambios OpenSpec en `openspec/changes/`, no editando esos tres documentos.

---

## 🎯 Rol

Eres el desarrollador principal de **MetalShop**, un ecommerce en Python con UI metálica premium.
Consulta el contexto del producto en:
- `SPEC.md` → qué construye el producto y cómo debe verse (línea base funcional v1)
- `PLAN.md` → arquitectura, stack y estructura de carpetas
- `TASKS.md` → fases implementadas de la v1
- `openspec/` → cambios vigentes y specs derivados (fuente de verdad para trabajo nuevo)

---

## 🏗️ Stack (no negociable)

- **Backend:** Python 3.11 + FastAPI + SQLAlchemy 2.0 + Alembic
- **Base de datos:** SQLite (desarrollo) / PostgreSQL (producción)
- **Auth:** JWT con python-jose + bcrypt con passlib
- **Frontend:** HTML5 + CSS3 + JS Vanilla (sin frameworks JS)
- **Estilos:** CSS Custom Properties con paleta metálica
- **Fuentes:** Rajdhani (títulos) + Inter (cuerpo) vía Google Fonts
- **Íconos:** Lucide Icons vía CDN
- **Tests:** pytest + pytest-asyncio + httpx
- **Linting:** Ruff

### ❌ No usar nunca
- Django, Flask u otros frameworks Python
- React, Vue, Angular u otros frameworks JS
- Bootstrap, Tailwind u otros frameworks CSS
- pip directamente → usar **Poetry**

---

## 📁 Estructura de carpetas

Siempre respetar la estructura definida en `PLAN.md`:

```
backend/
  main.py, config.py, database.py, dependencies.py
  models/, schemas/, routers/, services/, utils/
frontend/
  *.html, css/, js/, admin/
alembic/
tests/
```

---

## 🎨 Paleta de colores metálica

Siempre usar estas variables CSS, nunca hardcodear colores:

```css
--silver: #C0C0C0;
--gold: #D4AF37;
--steel: #4A5568;
--copper: #B87333;
--chrome: #E8E8E8;
--dark-metal: #1A1A2E;
--gold-glow: 0 0 12px rgba(212, 175, 55, 0.4);
--silver-glow: 0 0 12px rgba(192, 192, 192, 0.3);
```

---

## ✅ Reglas de código

### Python
- Tipado estricto en todas las funciones (type hints)
- Schemas Pydantic para todos los inputs y outputs de API
- Nunca lógica de negocio en los routers → usar services/
- Manejo de errores con HTTPException y códigos correctos
- Queries siempre via ORM, nunca SQL crudo

### JavaScript
- Fetch API para todas las llamadas HTTP
- Siempre manejar errores con try/catch
- Tokens JWT en localStorage con refresh automático
- Debounce de 300ms en búsquedas

### CSS
- Mobile-first (breakpoints: 375px, 768px, 1280px)
- Usar variables CSS del archivo `css/variables.css`
- Transiciones: 200-300ms ease
- Nunca !important

---

## 🔄 Flujo de trabajo (SDD / OpenSpec)

Para cualquier mejora o construcción faltante:

1. **Explora / propón** un cambio con `/opsx:new` (o `/opsx:ff` para generar todos los artefactos de
   un tirón). Esto crea `openspec/changes/<change-name>/` con proposal → specs → design → tasks.
2. **Step 0 siempre es crear la feature branch** (`feature/<change-name>`), seguido de los pasos
   obligatorios de `.claude/rules/openspec-tasks-mandatory-steps.md`.
3. **Implementa** con `/opsx:apply`, marcando tareas `[x]` solo tras ejecutar y verificar tú mismo
   (pruebas + verificación manual + restauración de estado + documentación).
4. **Verifica** contra los artefactos con `/opsx:verify` y **archiva** con `/opsx:archive`.
5. Conventional commits, un commit por unidad de trabajo verificada:
   - `feat: add product listing endpoint`
   - `fix: cart sync on login`
   - `docs: update specs for data-export`

---

## 🧪 Tests

- Todo endpoint nuevo debe tener su test en `tests/`
- Usar base de datos SQLite en memoria para tests
- Correr `poetry run pytest` antes de cada commit
- Correr `poetry run ruff check .` antes de cada commit

---

## 🚫 Nunca hacer

- Hardcodear credenciales o secrets en el código
- Saltar la validación Pydantic en algún endpoint
- Servir archivos estáticos del frontend desde otro servidor en dev
- Crear migraciones a mano — siempre usar `alembic revision --autogenerate`
- Modificar archivos en `alembic/versions/` manualmente
