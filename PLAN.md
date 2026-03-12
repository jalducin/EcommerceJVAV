# PLAN.md — Plan Técnico de Implementación
## MetalShop · Ecommerce en Python

---

## 1. Stack Tecnológico

### Backend
| Capa | Tecnología | Razón |
|---|---|---|
| Framework | **FastAPI** | Async, tipado, OpenAPI automático |
| ORM | **SQLAlchemy 2.0** + **Alembic** | Migraciones, relaciones |
| Base de datos | **PostgreSQL** | Relacional, producción |
| Dev DB | **SQLite** | Sin configuración local |
| Autenticación | **python-jose** + **passlib** | JWT + bcrypt |
| Email | **FastAPI-Mail** | SMTP, templates Jinja2 |
| Servidor | **Uvicorn** | ASGI, alta performance |

### Frontend
| Capa | Tecnología | Razón |
|---|---|---|
| Base | **HTML5 + CSS3 + JS Vanilla** | Sin build step, simple |
| Estilos | **CSS Custom Properties** | Variables metálicas, fácil theming |
| HTTP | **Fetch API** | Nativo, sin dependencias |
| Fuentes | **Google Fonts** (Rajdhani + Inter) | CDN gratuito |
| Íconos | **Lucide Icons** (CDN) | Ligero, SVG |

### Infra / Dev
| Herramienta | Uso |
|---|---|
| **Docker + Docker Compose** | Entorno reproducible |
| **Poetry** | Gestión de dependencias Python |
| **pytest** | Tests unitarios e integración |
| **Ruff** | Linting y formato |

---

## 2. Arquitectura

```
metalshop/
├── backend/
│   ├── main.py                  # Entry point FastAPI
│   ├── config.py                # Settings (pydantic-settings)
│   ├── database.py              # Engine + SessionLocal
│   ├── models/                  # SQLAlchemy models
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── order.py
│   │   └── cart.py
│   ├── schemas/                 # Pydantic schemas (request/response)
│   ├── routers/                 # Endpoints por módulo
│   │   ├── auth.py
│   │   ├── products.py
│   │   ├── cart.py
│   │   ├── orders.py
│   │   └── admin.py
│   ├── services/                # Lógica de negocio
│   ├── dependencies.py          # Auth middleware, DB session
│   └── utils/
│       ├── email.py
│       └── security.py
├── frontend/
│   ├── index.html               # Catálogo principal
│   ├── product.html             # Detalle de producto
│   ├── cart.html                # Carrito
│   ├── checkout.html            # Checkout
│   ├── login.html               # Auth
│   ├── orders.html              # Historial cliente
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── products.html
│   │   └── orders.html
│   ├── css/
│   │   ├── variables.css        # Tokens metálicos
│   │   ├── base.css
│   │   ├── components.css
│   │   └── pages/
│   └── js/
│       ├── api.js               # Fetch wrapper + auth headers
│       ├── cart.js
│       ├── auth.js
│       └── pages/
├── alembic/                     # Migraciones DB
├── tests/
├── docker-compose.yml
├── Dockerfile
└── pyproject.toml
```

---

## 3. Modelo de Datos

### Users
```
id, email (unique), hashed_password, full_name,
role (client|admin), created_at, is_active
```

### Products
```
id, name, description, price, stock, category,
images (JSON array), is_active, created_at
```

### Orders
```
id, user_id (FK), status (pending|shipped|delivered|cancelled),
total, shipping_address (JSON), created_at
```

### OrderItems
```
id, order_id (FK), product_id (FK), quantity, unit_price
```

### Cart (persistida para usuarios autenticados)
```
id, user_id (FK), product_id (FK), quantity
```

---

## 4. API Endpoints Principales

```
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/refresh

GET    /api/products              # Catálogo público (filtros, búsqueda, paginación)
GET    /api/products/{id}         # Detalle
POST   /api/products              # Admin only
PUT    /api/products/{id}         # Admin only
DELETE /api/products/{id}         # Admin only

GET    /api/cart                  # Cart del usuario autenticado
POST   /api/cart/items
PUT    /api/cart/items/{id}
DELETE /api/cart/items/{id}

POST   /api/orders/checkout
GET    /api/orders                # Historial del cliente
GET    /api/orders/{id}

GET    /api/admin/dashboard       # Métricas
GET    /api/admin/orders          # Todos los pedidos
PATCH  /api/admin/orders/{id}/status
```

---

## 5. Seguridad

- Contraseñas hasheadas con **bcrypt** (cost factor 12)
- JWT firmados con HS256, secret en variables de entorno
- Rate limiting: 5 intentos de login por IP cada 15 min
- CORS configurado por entorno (dev: *, prod: dominio específico)
- Validación de inputs con Pydantic en todos los endpoints
- SQL injection imposible via ORM (queries parametrizadas)

---

## 6. Variables de Entorno

```env
DATABASE_URL=postgresql://user:pass@localhost/metalshop
SECRET_KEY=<256-bit-random>
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@metalshop.com
SMTP_PASSWORD=<app-password>
ENVIRONMENT=development
```

---

## 7. CI/CD

### Pipeline GitHub Actions (`.github/workflows/ci.yml`)

Se ejecuta en cada push a `main`/`develop` y en pull requests:

1. Checkout + Python 3.11 + Poetry (con caché de dependencias)
2. `ruff check .` — linting y formato
3. `pytest -v --tb=short` — suite completa con SQLite in-memory

### Estrategia de deploy

| Entorno | Servidor | BD | Config |
|---|---|---|---|
| **Dev local** | `uvicorn --reload` | SQLite | `.env` con defaults |
| **Docker local** | `uvicorn` (stage dev) | PostgreSQL via Compose | `.env` personalizado |
| **Producción** | Gunicorn + 4 UvicornWorkers | PostgreSQL | Variables de entorno del servidor |

El frontend se sirve como archivos estáticos desde FastAPI (`StaticFiles` montado en `/`), eliminando la necesidad de un servidor web separado (nginx) para el frontend en despliegues simples.
