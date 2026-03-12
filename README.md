# MetalShop — Ecommerce en Python con UI Metálica

> Tienda en línea construida con **Python + FastAPI** y un frontend estático con estética metálica premium (plata, oro, acero, cobre).

[![CI](https://github.com/jalducin/EcommerceJVAV/actions/workflows/ci.yml/badge.svg)](https://github.com/jalducin/EcommerceJVAV/actions/workflows/ci.yml)

---

## Visión del Producto

**MetalShop** es una tienda en línea de equipamiento y herramientas. Orientada a venta de productos con una experiencia visual de alto impacto — gradientes metálicos, brillos dorados, tipografía Rajdhani.

---

## Stack Tecnológico

### Backend
| Capa | Tecnología |
|---|---|
| Framework | **FastAPI 0.115** + Uvicorn (ASGI) |
| ORM | **SQLAlchemy 2.0** + Alembic (migraciones) |
| Base de datos | **SQLite** (dev) / **PostgreSQL** (prod) |
| Autenticación | **python-jose** (JWT HS256) + **passlib** (bcrypt) |
| Validación | **Pydantic v2** con type hints estrictos |
| Email | FastAPI-Mail + Jinja2 templates |
| Rate limiting | **slowapi** — protección endpoint login |

### Frontend
| Capa | Tecnología |
|---|---|
| Base | **HTML5 + CSS3 + JavaScript Vanilla** (sin frameworks) |
| Estilos | **CSS Custom Properties** — paleta metálica |
| HTTP | **Fetch API** nativo con refresh automático de JWT |
| Fuentes | **Google Fonts**: Rajdhani (títulos) + Inter (cuerpo) |
| Íconos | **Lucide Icons** (CDN) |

### Dev / Infra
| Herramienta | Uso |
|---|---|
| **Poetry** | Gestión de dependencias Python |
| **Docker + Compose** | Entorno reproducible (app + postgres) |
| **pytest + httpx** | Tests asíncronos con SQLite in-memory |
| **Ruff** | Linting + formato |
| **GitHub Actions** | CI: lint + tests en cada push/PR |

---

## Paleta de Colores Metálica

```css
--silver:     #C0C0C0   /* Fondos secundarios, bordes */
--gold:       #D4AF37   /* CTAs principales, highlights */
--steel:      #4A5568   /* Navbar, texturas base */
--copper:     #B87333   /* Acentos, badges */
--chrome:     #E8E8E8   /* Cards, superficies */
--dark-metal: #1A1A2E   /* Fondo principal */
```

---

## Estructura del Proyecto

```
metalshop/
├── backend/
│   ├── main.py               # FastAPI app + routers + archivos estáticos
│   ├── config.py             # Settings con pydantic-settings (lectura de .env)
│   ├── database.py           # Engine async, SessionLocal, Base declarativa
│   ├── dependencies.py       # get_current_user, require_admin, get_db
│   ├── limiter.py            # Instancia slowapi para rate limiting
│   ├── models/               # SQLAlchemy models (User, Product, Order, CartItem)
│   ├── schemas/              # Pydantic schemas (auth, product, cart, order)
│   ├── routers/              # Endpoints por módulo
│   │   ├── auth.py           # /api/auth/*
│   │   ├── products.py       # /api/products/*
│   │   ├── cart.py           # /api/cart/*
│   │   ├── orders.py         # /api/orders/*
│   │   └── admin.py          # /api/admin/*
│   ├── services/             # Lógica de negocio (sin lógica en routers)
│   └── utils/
│       ├── security.py       # JWT, bcrypt, hash/verify
│       └── email.py          # Templates y envío de emails
├── frontend/
│   ├── index.html            # Catálogo principal
│   ├── product.html          # Detalle de producto
│   ├── cart.html             # Página de carrito
│   ├── checkout.html         # Checkout con formulario de envío
│   ├── order-confirm.html    # Confirmación de pedido
│   ├── login.html            # Login / Registro (tabs metálicos)
│   ├── orders.html           # Historial de pedidos del cliente
│   ├── forgot-password.html  # Recuperación de contraseña
│   ├── admin/
│   │   ├── dashboard.html    # Métricas y gráfica de ventas
│   │   ├── products.html     # CRUD de productos
│   │   └── orders.html       # Gestión de pedidos
│   ├── css/
│   │   ├── variables.css     # Tokens metálicos (colores, sombras, gradientes)
│   │   ├── base.css          # Reset, tipografía, navbar, footer, toasts
│   │   └── components.css    # Cards, botones, badges, modales, drawer
│   └── js/
│       ├── api.js            # Fetch wrapper + JWT refresh automático
│       ├── auth.js           # Navbar dinámica, guards requireAuth/requireAdmin
│       ├── cart.js           # Carrito dual (localStorage ↔ API)
│       └── pages/
│           ├── catalog.js    # Filtros, búsqueda debounce 300ms, paginación
│           ├── product.js    # Galería, selector qty, add to cart
│           ├── login.js      # Login/registro, strength bar, sync carrito
│           ├── checkout.js   # Validación formulario, POST checkout
│           ├── orders.js     # Historial con detalle expandible y timeline
│           └── forgot-password.js
├── alembic/                  # Migraciones de base de datos
│   ├── env.py
│   └── versions/
├── tests/
│   ├── conftest.py           # Fixtures: SQLite in-memory, AsyncClient
│   ├── test_auth.py          # Registro, login, refresh, rutas protegidas
│   ├── test_products.py      # CRUD, filtros, paginación
│   ├── test_cart.py          # Agregar, actualizar, eliminar, sync
│   ├── test_orders.py        # Checkout con/sin stock
│   └── test_admin.py         # Acceso con y sin rol admin
├── .github/
│   └── workflows/
│       └── ci.yml            # CI: ruff + pytest en cada push/PR
├── seed_products.py          # 20 productos de ejemplo
├── pyproject.toml            # Dependencias Poetry + config Ruff + pytest
├── Dockerfile                # Multi-stage: development + production (gunicorn)
├── docker-compose.yml        # Servicios: app + postgres con healthcheck
└── .env.example              # Variables de entorno documentadas
```

---

## Despliegue Local (paso a paso)

### Requisitos previos

| Herramienta | Versión mínima | Verificar |
|---|---|---|
| Python | 3.11 | `python --version` |
| Poetry | 1.8+ | `poetry --version` |
| Git | cualquiera | `git --version` |

> **¿No tienes Poetry?** Instálalo con: `pip install poetry`

### Opción A — Local con SQLite (más rápido, sin Docker)

Es la forma más sencilla. Usa SQLite como base de datos — no necesitas instalar nada más.

```bash
# 1. Clonar el repositorio
git clone https://github.com/jalducin/EcommerceJVAV.git
cd EcommerceJVAV

# 2. Instalar dependencias Python
poetry install

# 3. Configurar variables de entorno
cp .env.example .env
# El archivo .env ya apunta a SQLite por defecto — no necesitas cambiar nada para desarrollo

# 4. Aplicar migraciones (crea la base de datos y las tablas)
poetry run alembic upgrade head

# 5. Poblar la base de datos con 20 productos de ejemplo
poetry run python seed_products.py

# 6. Levantar el servidor de desarrollo
poetry run uvicorn backend.main:app --reload
```

La app queda disponible en:
- **Frontend:** `http://localhost:8000`
- **API Docs (Swagger):** `http://localhost:8000/api/docs`
- **API Docs (ReDoc):** `http://localhost:8000/api/redoc`

### Opción B — Docker Compose con PostgreSQL (recomendado para producción local)

Requiere tener Docker Desktop instalado y corriendo.

```bash
# 1. Clonar el repositorio
git clone https://github.com/jalducin/EcommerceJVAV.git
cd EcommerceJVAV

# 2. Configurar variables de entorno
cp .env.example .env
# Edita .env y descomenta la línea de PostgreSQL:
#   DATABASE_URL=postgresql+asyncpg://metalshop:metalshop@db:5432/metalshop

# 3. Construir y levantar los servicios (app + postgres)
docker compose up --build

# 4. En otra terminal — aplicar migraciones
docker compose exec app poetry run alembic upgrade head

# 5. Poblar con productos de ejemplo
docker compose exec app poetry run python seed_products.py
```

La app queda disponible en `http://localhost:8000`.

### Crear usuario administrador

Una vez levantado el servidor, registra un usuario y cambia su rol directamente en la BD:

**Con SQLite:**
```bash
# Registrar el usuario vía API
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@metalshop.com", "password": "Admin1234!", "full_name": "Administrador"}'

# Promover a admin (requiere sqlite3 instalado)
sqlite3 metalshop.db "UPDATE users SET role='admin' WHERE email='admin@metalshop.com';"
```

**Con Docker + PostgreSQL:**
```bash
docker compose exec db psql -U metalshop -d metalshop \
  -c "UPDATE users SET role='admin' WHERE email='admin@metalshop.com';"
```

Ahora puedes acceder al panel en `http://localhost:8000/admin/dashboard.html`.

---

## Migraciones con Alembic

```bash
# Generar nueva migración desde cambios en los modelos
poetry run alembic revision --autogenerate -m "descripcion_del_cambio"

# Aplicar todas las migraciones pendientes
poetry run alembic upgrade head

# Revertir la última migración
poetry run alembic downgrade -1

# Ver historial de migraciones
poetry run alembic history
```

---

## API Endpoints

### Autenticación
| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/auth/register` | Registrar usuario (email único, pass ≥8 chars) |
| `POST` | `/api/auth/login` | Login → devuelve access + refresh token |
| `POST` | `/api/auth/refresh` | Renovar access token con refresh token |
| `GET`  | `/api/auth/me` | Perfil del usuario autenticado |

### Productos (catálogo público)
| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET`  | `/api/products` | Listado con filtros: `search`, `category`, `min_price`, `max_price`, `limit`, `offset` |
| `GET`  | `/api/products/{id}` | Detalle de producto |
| `POST` | `/api/products` | Crear producto _(solo admin)_ |
| `PUT`  | `/api/products/{id}` | Actualizar parcialmente _(solo admin)_ |
| `DELETE` | `/api/products/{id}` | Soft delete _(solo admin)_ |

### Carrito _(requiere auth)_
| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET`  | `/api/cart` | Carrito del usuario con totales |
| `POST` | `/api/cart/items` | Agregar ítem (merge si ya existe) |
| `PUT`  | `/api/cart/items/{id}` | Actualizar cantidad |
| `DELETE` | `/api/cart/items/{id}` | Eliminar ítem |
| `POST` | `/api/cart/sync` | Fusionar carrito localStorage → BD |

### Pedidos _(requiere auth)_
| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/orders/checkout` | Crear pedido (valida stock, descuenta inventario) |
| `GET`  | `/api/orders` | Historial del usuario |
| `GET`  | `/api/orders/{id}` | Detalle con ítems |

### Admin _(requiere rol admin)_
| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET`  | `/api/admin/dashboard` | Métricas: ventas hoy, pedidos pendientes, bajo stock |
| `GET`  | `/api/admin/orders` | Todos los pedidos con paginación y filtro por estado |
| `PATCH` | `/api/admin/orders/{id}/status` | Cambiar estado del pedido |

---

## Tests

```bash
# Ejecutar todos los tests
poetry run pytest -v

# Con reporte de coverage
poetry run pytest --cov=backend --cov-report=term-missing

# Linting
poetry run ruff check .

# Solo un módulo específico
poetry run pytest tests/test_auth.py -v
```

Los tests usan **SQLite en memoria** — sin necesidad de base de datos externa.

| Archivo | Cobertura |
|---|---|
| `tests/test_auth.py` | Registro, login, refresh, rutas protegidas |
| `tests/test_products.py` | CRUD, filtros, paginación |
| `tests/test_cart.py` | Agregar, actualizar, eliminar, sync |
| `tests/test_orders.py` | Checkout con stock suficiente e insuficiente |
| `tests/test_admin.py` | Acceso con y sin rol admin |

---

## CI/CD

El proyecto incluye un pipeline de GitHub Actions en `.github/workflows/ci.yml` que se ejecuta automáticamente en cada push a `main`/`develop` y en pull requests:

1. Checkout del código
2. Configurar Python 3.11
3. Instalar dependencias con Poetry (con caché)
4. `ruff check .` — linting y formato
5. `pytest -v` — suite completa de tests con SQLite in-memory

---

## Deploy a Producción

### 1. Configurar variables de entorno de producción

```env
ENVIRONMENT=production
FRONTEND_URL=https://tu-dominio.com

DATABASE_URL=postgresql+asyncpg://metalshop:PASSWORD@db:5432/metalshop

# Genera con: openssl rand -hex 32
SECRET_KEY=TU_SECRET_KEY_DE_PRODUCCION_SUPER_SEGURO

SMTP_HOST=smtp.tu-proveedor.com
SMTP_PORT=587
SMTP_USER=tu-usuario-smtp
SMTP_PASSWORD=tu-password-smtp
EMAILS_FROM=noreply@tu-dominio.com
```

### 2. Levantar con Docker Compose (stage production)

```bash
# Construir con el stage production (gunicorn + 4 workers uvicorn)
docker compose up --build -d

# Aplicar migraciones
docker compose exec app poetry run alembic upgrade head

# (Opcional) Datos de ejemplo
docker compose exec app poetry run python seed_products.py
```

La imagen de producción usa **Gunicorn** como process manager con workers Uvicorn (`-w 4`).

---

## Seguridad

- Contraseñas hasheadas con **bcrypt** (cost factor 12)
- JWT firmados con **HS256**, secret en `.env`
- Access token: **30 min** · Refresh token: **7 días**
- `type` claim en JWT diferencia access de refresh tokens
- Rate limiting en `/api/auth/login`: máximo 5 intentos por IP cada 15 min (slowapi)
- Validación de inputs con Pydantic en **todos** los endpoints
- SQL injection imposible — queries 100% vía ORM
- CORS: `*` en dev, dominio específico en producción

---

## Variables de Entorno

| Variable | Default (dev) | Descripción |
|---|---|---|
| `ENVIRONMENT` | `development` | `development` o `production` |
| `FRONTEND_URL` | `http://localhost:8000` | URL para CORS |
| `DATABASE_URL` | `sqlite+aiosqlite:///./metalshop.db` | Conexión a la BD |
| `SECRET_KEY` | — | Clave para firmar JWT (obligatoria) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Vida del access token |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Vida del refresh token |
| `SMTP_HOST` | — | Servidor SMTP (opcional en dev) |
| `SMTP_PORT` | `587` | Puerto SMTP |
| `SMTP_USER` | — | Usuario SMTP |
| `SMTP_PASSWORD` | — | Contraseña SMTP |
| `EMAILS_FROM` | `noreply@metalshop.com` | Remitente de emails |

---

## Estado del Proyecto

| Fase | Descripción | Estado |
|------|-------------|--------|
| **Fase 1** | Setup: FastAPI, config, DB, Alembic, Docker | Completada |
| **Fase 2** | Modelos SQLAlchemy + Autenticación JWT | Completada |
| **Fase 3** | Productos, Catálogo y Frontend base | Completada |
| **Fase 4** | Carrito y Checkout | Completada |
| **Fase 5** | Auth Frontend + Historial de pedidos | Completada |
| **Fase 6** | Panel Administrador | Completada |
| **Fase 7** | Email + Rate limiting + Pulido UI | Completada |
| **Fase 8** | Tests completos + CI + Deploy | Completada |

---

## Roles de Usuario

| Rol | Capacidades |
|-----|-------------|
| **Visitante** | Navega catálogo, carrito en localStorage |
| **Cliente** | Compras, historial de pedidos, carrito persistido en BD |
| **Admin** | CRUD productos, gestión de pedidos, dashboard de métricas |

---

## Backlog (v2)

- Subida real de imágenes (AWS S3 o Cloudflare R2)
- Integración con Stripe para pagos reales
- Sistema de reseñas y ratings por producto
- Wishlist / lista de deseos
- Cupones de descuento
- Notificaciones en tiempo real (WebSockets) para admin
- PWA con Service Worker para uso offline
- Internacionalización (ES/EN)

---

## Licencia

MIT — Proyecto educativo / portafolio.
