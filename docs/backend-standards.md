---
description: Estándares de backend de MetalShop (Python / FastAPI / SQLAlchemy / Alembic / pytest / Ruff / seguridad).
alwaysApply: true
---

# Estándares de backend — MetalShop

> Complementa `base-standards.md` y `documentation-standards.md`. Aplica a todo cambio que toque
> `backend/`, `alembic/`, `tests/` o la configuración del servidor.

## 1. Stack (no negociable)

- Python 3.11 + FastAPI + SQLAlchemy 2.0 + Alembic.
- Base de datos: SQLite (desarrollo) / PostgreSQL (producción).
- Auth: JWT con python-jose + bcrypt con passlib. Email: FastAPI-Mail. Rate limiting: slowapi.
- Servidor: Uvicorn (dev) / Gunicorn + UvicornWorker (prod).
- Tests: pytest + pytest-asyncio + httpx. Lint/formato: Ruff. Dependencias: Poetry.

### Prohibido
- Django, Flask u otros frameworks Python.
- `pip` directo → usar **Poetry**.
- SQL crudo → siempre vía ORM (queries parametrizadas).

## 2. Arquitectura por capas

```
backend/
  main.py            # instancia FastAPI (app real: backend.main:app)
  config.py          # settings con pydantic-settings (lee .env)
  database.py        # engine + SessionLocal + Base declarativa
  dependencies.py    # get_db(), get_current_user, require_admin
  limiter.py         # slowapi
  models/            # SQLAlchemy: user, product, order, cart
  schemas/           # Pydantic (request/response)
  routers/           # endpoints por módulo: auth, products, cart, orders, admin
  services/          # lógica de negocio
  utils/             # email, security
```

- **La lógica de negocio vive en `services/`, nunca en los routers.** Los routers solo validan,
  delegan al service y mapean respuestas/errores.
- El frontend estático se sirve desde FastAPI con `StaticFiles`; no usar otro servidor en dev.

## 3. Reglas de código Python

- Tipado estricto en todas las funciones (type hints).
- Schemas Pydantic para **todos** los inputs y outputs de API — nunca saltar la validación.
- Manejo de errores con `HTTPException` y el código HTTP correcto.
- Queries siempre vía ORM (SQLAlchemy), nunca SQL crudo.
- Nunca hardcodear credenciales o secrets; leerlos desde `config.py` / variables de entorno.

## 4. Migraciones (Alembic)

- Crear migraciones **solo** con `alembic revision --autogenerate -m "<mensaje>"`.
- Nunca editar a mano los archivos de `alembic/versions/`.
- Aplicar con `alembic upgrade head`.

## 5. Seguridad

- Contraseñas con bcrypt (cost factor 12). JWT HS256, secret en variables de entorno.
- Access token 30 min + refresh token 7 días. Rate limiting en login.
- CORS por entorno (dev: `*`, prod: dominio específico).
- Validación de inputs con Pydantic en todos los endpoints.

## 6. Pruebas y verificación (OBLIGATORIO antes de cada commit)

- Todo endpoint nuevo o modificado debe tener su test en `tests/`.
- Usar base de datos SQLite **en memoria** para tests (ver `tests/conftest.py`).
- Comandos de verificación que el agente DEBE ejecutar él mismo:
  - `poetry run ruff check .` — sin errores.
  - `poetry run pytest` — toda la suite en verde.
- Verificación manual de API (Step N+2 de la regla de tasks): probar endpoints (status + cuerpo),
  cubrir casos de error (inválidos, inexistentes, permisos) y restaurar estado tras CREATE/UPDATE/DELETE.

## 7. API

- Endpoints bajo `/api`: `auth`, `products`, `cart`, `orders`, `admin`.
- FastAPI genera OpenAPI automáticamente; mantener `title`/`version`/descripciones al día.
