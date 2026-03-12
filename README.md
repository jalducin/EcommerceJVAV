# ⚙ MetalShop — Ecommerce en Python con UI Metálica

> Tienda en línea construida con **Python + FastAPI** y un frontend estático con estética metálica premium (plata, oro, acero, cobre).

---

## 🎯 Visión del Producto

**MetalShop** es una tienda en línea de equipamiento y herramientas metálicas de calidad industrial. Orientada a venta de productos con una experiencia visual de alto impacto — gradientes metálicos, brillos dorados, tipografía Rajdhani.

---

## 🏗️ Stack Tecnológico

### Backend
| Capa | Tecnología |
|---|---|
| Framework | **FastAPI 0.115** + Uvicorn (ASGI) |
| ORM | **SQLAlchemy 2.0** + Alembic (migraciones) |
| Base de datos | **SQLite** (dev) / **PostgreSQL** (prod) |
| Autenticación | **python-jose** (JWT HS256) + **passlib** (bcrypt) |
| Validación | **Pydantic v2** con type hints estrictos |
| Email | FastAPI-Mail + Jinja2 templates |

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

---

## 🎨 Paleta de Colores Metálica

```css
--silver:     #C0C0C0   /* Fondos secundarios, bordes */
--gold:       #D4AF37   /* CTAs principales, highlights */
--steel:      #4A5568   /* Navbar, texturas base */
--copper:     #B87333   /* Acentos, badges */
--chrome:     #E8E8E8   /* Cards, superficies */
--dark-metal: #1A1A2E   /* Fondo principal */
```

---

## 📁 Estructura del Proyecto

```
metalshop/
├── backend/
│   ├── main.py               # FastAPI app + routers + static files
│   ├── config.py             # Settings pydantic-settings (.env)
│   ├── database.py           # Engine async, SessionLocal, Base
│   ├── dependencies.py       # get_current_user, require_admin
│   ├── models/               # SQLAlchemy models (User, Product, Order, Cart)
│   ├── schemas/              # Pydantic schemas (auth, product, cart, order)
│   ├── routers/              # Endpoints por módulo
│   │   ├── auth.py           # /api/auth/*
│   │   ├── products.py       # /api/products/*
│   │   ├── cart.py           # /api/cart/*
│   │   └── orders.py         # /api/orders/*
│   ├── services/             # Lógica de negocio (sin lógica en routers)
│   └── utils/
│       └── security.py       # JWT, bcrypt, hash/verify
├── frontend/
│   ├── index.html            # Catálogo principal
│   ├── product.html          # Detalle de producto
│   ├── cart.html             # Página de carrito
│   ├── checkout.html         # Checkout con formulario de envío
│   ├── order-confirm.html    # Confirmación de pedido (confetti)
│   ├── login.html            # Login / Registro (tabs metálicos)
│   ├── orders.html           # Historial de pedidos del cliente
│   ├── admin/                # Panel administrador (Fase 6)
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
│           ├── product.js    # Galería, qty selector, add to cart
│           ├── login.js      # Login/registro, strength bar, sync carrito
│           ├── checkout.js   # Validación formulario, POST checkout
│           └── orders.js     # Historial con detalle expandible y timeline
├── alembic/                  # Migraciones de base de datos
├── tests/
│   ├── conftest.py           # Fixtures: SQLite in-memory, AsyncClient
│   └── test_auth.py          # 11 tests de autenticación
├── seed_products.py          # 20 productos de ejemplo
├── pyproject.toml            # Dependencias Poetry + Ruff config
├── Dockerfile                # Multi-stage: development + production
├── docker-compose.yml        # app + postgres con healthcheck
└── .env.example              # Variables de entorno documentadas
```

---

## 🚀 Inicio Rápido

### Opción A — Docker (recomendado)

```bash
# Clonar y configurar entorno
cp .env.example .env

# Levantar servicios (app + postgres)
docker compose up --build

# En otra terminal — poblar BD con productos de ejemplo
docker compose exec app python seed_products.py
```

API disponible en: `http://localhost:8000`
Docs interactivos: `http://localhost:8000/api/docs`

### Opción B — Local con Poetry + SQLite

```bash
# Instalar dependencias
poetry install

# Configurar entorno
cp .env.example .env
# DATABASE_URL=sqlite+aiosqlite:///./metalshop.db  (ya es el default)

# Ejecutar app
poetry run uvicorn backend.main:app --reload

# Poblar BD
poetry run python seed_products.py
```

---

## 🗄️ Migraciones con Alembic

```bash
# Generar migración desde los modelos
poetry run alembic revision --autogenerate -m "nombre_descripcion"

# Aplicar migraciones
poetry run alembic upgrade head

# Revertir última migración
poetry run alembic downgrade -1
```

---

## 🔌 API Endpoints

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

---

## 🧪 Tests

```bash
# Ejecutar todos los tests
poetry run pytest -v

# Con coverage
poetry run pytest --cov=backend --cov-report=term-missing

# Linting
poetry run ruff check .
```

Los tests usan **SQLite en memoria** — sin necesidad de BD externa.

---

## 🔐 Seguridad

- Contraseñas hasheadas con **bcrypt** (cost factor 12)
- JWT firmados con **HS256**, secret en `.env`
- Access token: **30 min** · Refresh token: **7 días**
- `type` claim en JWT diferencia access de refresh tokens
- Validación de inputs con Pydantic en **todos** los endpoints
- SQL injection imposible — queries 100% vía ORM
- CORS: `*` en dev, dominio específico en producción

---

## 🌍 Variables de Entorno

```env
# App
ENVIRONMENT=development
FRONTEND_URL=http://localhost:8000

# Base de datos
DATABASE_URL=sqlite+aiosqlite:///./metalshop.db
# PostgreSQL: postgresql+asyncpg://user:pass@localhost/metalshop

# JWT — genera con: openssl rand -hex 32
SECRET_KEY=cambia-esto-en-produccion
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email (opcional en dev)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu@gmail.com
SMTP_PASSWORD=tu-app-password
EMAILS_FROM=noreply@metalshop.com
```

---

## 📊 Estado del Proyecto

| Fase | Descripción | Estado |
|------|-------------|--------|
| **Fase 1** | Setup y Base (FastAPI, config, DB, Alembic, Docker) | ✅ Completada |
| **Fase 2** | Modelos SQLAlchemy + Autenticación JWT | ✅ Completada |
| **Fase 3** | Productos, Catálogo y Frontend base | ✅ Completada |
| **Fase 4** | Carrito y Checkout | ✅ Completada |
| **Fase 5** | Auth Frontend (login/registro) + Historial de pedidos | ✅ Completada |
| **Fase 6** | Panel Administrador | 🔲 Pendiente |
| **Fase 7** | Email de confirmación + Rate limiting + Pulido | 🔲 Pendiente |
| **Fase 8** | Tests completos + Deploy | 🔲 Pendiente |

---

## 👥 Roles de Usuario

| Rol | Capacidades |
|-----|-------------|
| **Visitante** | Navega catálogo, carrito en localStorage |
| **Cliente** | Compras, historial de pedidos, carrito persistido en BD |
| **Admin** | CRUD productos, gestión de pedidos, dashboard de métricas |

---

## 📋 Módulos Funcionales

### ✅ Implementados
- **Catálogo** — Grid de productos, filtros por categoría/precio, búsqueda en tiempo real (debounce 300ms), paginación
- **Detalle de producto** — Galería de imágenes, selector de cantidad, badge de stock
- **Carrito** — Dual mode localStorage (visitante) / API (autenticado), drawer slide-in, sync al login
- **Checkout** — Formulario de envío validado, selección de método de pago, resumen del pedido
- **Confirmación** — Número de orden, timeline de estado, animación confetti
- **Autenticación** — Login / Registro con tabs, strength bar, JWT con refresh automático
- **Historial** — Órdenes con filtros por estado, detalle expandible, timeline visual

### 🔲 Próximos
- **Panel Admin** — Dashboard métricas, CRUD productos, gestión de pedidos
- **Email** — Confirmación de pedido en HTML metálico
- **Rate limiting** — Protección endpoint login (slowapi)

---

## 📄 Licencia

MIT — Proyecto educativo / portafolio.
