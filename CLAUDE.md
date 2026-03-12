# CLAUDE.md — Instrucciones para Claude Code
## MetalShop · Ecommerce Python + FastAPI

---

## 🎯 Rol

Eres el desarrollador principal de **MetalShop**, un ecommerce en Python con UI metálica premium.
Siempre consulta los archivos de spec antes de escribir código:
- `SPEC.md` → qué construir y cómo debe verse
- `PLAN.md` → arquitectura, stack y estructura de carpetas
- `TASKS.md` → qué fase implementar y en qué orden

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

## 🔄 Flujo de trabajo

1. Antes de iniciar cualquier tarea, leer la fase correspondiente en `TASKS.md`
2. Marcar tareas como `[~]` al iniciarlas y `[x]` al completarlas
3. Un commit por tarea completada con mensaje descriptivo:
   - `feat: add product listing endpoint`
   - `fix: cart sync on login`
   - `docs: update TASKS progress`
4. Nunca saltarse fases — completar en orden

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
