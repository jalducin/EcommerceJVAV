# Contexto del proyecto — MetalShop

Este documento da contexto a los agentes de IA sobre el proyecto.

## Qué es

**MetalShop** es una tienda en línea (ecommerce) construida con Python/FastAPI y un frontend estático
con estética metálica premium (plata, oro, acero, cobre). Cubre catálogo, carrito, checkout,
autenticación, historial de pedidos y panel de administración. En v1 no procesa pagos reales (modo
simulado). Pensada para venta de productos genéricos con una experiencia visual de alto impacto.

## Stack tecnológico

- Lenguaje: Python 3.11.
- Framework backend: FastAPI + SQLAlchemy 2.0 + Alembic (migraciones).
- Base de datos: SQLite (desarrollo) / PostgreSQL (producción).
- Frontend: HTML5 + CSS3 + JavaScript Vanilla (sin frameworks), CSS Custom Properties, Fetch API.
- Auth: JWT (python-jose) + bcrypt (passlib). Email: FastAPI-Mail. Rate limiting: slowapi.
- Servidor: Uvicorn (dev) / Gunicorn + Uvicorn workers (prod).
- Tests: pytest + pytest-asyncio + httpx (SQLite in-memory). Lint/formato: Ruff.
- Tooling: Poetry (dependencias), Docker + Docker Compose.
- Fuentes: Rajdhani (títulos) + Inter (cuerpo) vía Google Fonts. Íconos: Lucide (CDN).

## Arquitectura

Backend por capas en `backend/`: `models/` (SQLAlchemy) → `schemas/` (Pydantic) → `routers/` (endpoints)
→ `services/` (lógica de negocio) → `utils/`. La lógica de negocio vive en `services/`, nunca en los
routers. Las queries siempre vía ORM. El frontend estático se sirve desde FastAPI con `StaticFiles`.

API principal bajo `/api`: `auth`, `products`, `cart`, `orders`, `admin`. Modelo de datos: `User`,
`Product`, `Order` + `OrderItem`, `CartItem`. Detalle en `PLAN.md`.

## Convenciones

- Idioma: documentación y comentarios en español; identificadores de código en inglés.
- Commits: conventional commits.
- Ramas: `feature/<change-name>`.
- Estándares por área en `docs/*-standards.md` (backend, frontend, base, documentación).
- Nunca: hardcodear secrets, saltar validación Pydantic, SQL crudo, frameworks JS/CSS,
  editar migraciones a mano (usar `alembic revision --autogenerate`).

## Comandos clave

- Instalar dependencias: `poetry install`
- Ejecutar pruebas: `poetry run pytest`
- Lint: `poetry run ruff check .`
- Levantar el proyecto (dev): `poetry run uvicorn backend.main:app --reload`
- Levantar con Docker: `docker-compose up`
- Migraciones: `poetry run alembic revision --autogenerate -m "<mensaje>"` y `poetry run alembic upgrade head`
- Seed de productos: `poetry run python seed_products.py`
