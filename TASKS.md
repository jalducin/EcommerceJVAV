# TASKS.md — Tareas de Implementación
## MetalShop · Ecommerce en Python

> Convención de estados: `[ ]` pendiente · `[~]` en progreso · `[x]` completado

---

## FASE 1 — Setup y Base (Días 1-2)

### Entorno
- [x] Inicializar proyecto con `poetry init` y definir dependencias base
- [x] Configurar `pyproject.toml` con Ruff (linting + formato)
- [x] Crear `docker-compose.yml` con servicios: app, postgres
- [x] Crear `Dockerfile` multi-stage (dev + prod)
- [x] Configurar `.env.example` con todas las variables necesarias
- [x] Inicializar repositorio Git con `.gitignore` apropiado

### Backend Base
- [x] Crear instancia FastAPI en `main.py` con metadata (título, versión, docs)
- [x] Configurar `config.py` con pydantic-settings (lectura de `.env`)
- [x] Configurar `database.py`: engine, SessionLocal, Base declarativa
- [x] Crear `dependencies.py`: `get_db()` session injector
- [x] Inicializar Alembic (`alembic init alembic`)
- [x] Configurar `alembic/env.py` para leer `DATABASE_URL` del entorno

---

## FASE 2 — Modelos y Auth (Días 3-4)

### Modelos SQLAlchemy
- [x] Modelo `User`: id, email, hashed_password, full_name, role, created_at, is_active
- [x] Modelo `Product`: id, name, description, price, stock, category, images, is_active
- [x] Modelo `Order` + `OrderItem`: relación one-to-many
- [x] Modelo `CartItem`: user_id + product_id + quantity
- [x] Crear y ejecutar migración inicial con Alembic

### Autenticación
- [x] Schemas Pydantic: `UserCreate`, `UserLogin`, `UserResponse`, `Token`
- [x] Utilidades en `utils/security.py`: hash password, verify password, create JWT, decode JWT
- [x] Endpoint `POST /api/auth/register` con validación de email único
- [x] Endpoint `POST /api/auth/login` → devuelve access + refresh token
- [x] Endpoint `POST /api/auth/refresh` → renueva access token
- [x] Dependency `get_current_user` para rutas protegidas
- [x] Dependency `require_admin` para rutas de admin
- [x] Tests unitarios: registro, login, token inválido, token expirado

---

## FASE 3 — Productos y Catálogo (Días 5-6)

### Backend
- [x] Schemas: `ProductCreate`, `ProductUpdate`, `ProductResponse`, `ProductList`
- [x] `GET /api/products`: paginación (limit/offset), filtro por categoría, búsqueda por nombre, filtro por precio min/max
- [x] `GET /api/products/{id}`: detalle con stock actual
- [x] `POST /api/products`: solo admin, validar precio > 0, stock >= 0
- [x] `PUT /api/products/{id}`: solo admin, actualización parcial
- [x] `DELETE /api/products/{id}`: soft delete (is_active = False)
- [x] Script seed: `seed_products.py` con 20 productos de ejemplo

### Frontend — Catálogo
- [x] Crear `css/variables.css` con todos los tokens metálicos (colores, sombras, gradientes)
- [x] Crear `css/base.css`: reset, tipografía Rajdhani + Inter, layout base
- [x] Crear `css/components.css`: card, button, badge, input, modal, drawer
- [x] Diseñar y construir `index.html`: navbar + hero + grid de productos + filtros sidebar
- [x] `js/api.js`: wrapper de fetch con base URL, headers de auth, manejo de errores
- [x] `js/pages/catalog.js`: cargar productos, filtros reactivos, búsqueda con debounce
- [x] Diseñar y construir `product.html`: galería, descripción, botón agregar al carrito
- [x] Animaciones CSS: hover cards (elevación + brillo metálico), loading skeleton

---

## FASE 4 — Carrito y Checkout (Días 7-8)

### Backend
- [x] Schemas: `CartItemCreate`, `CartItemUpdate`, `CartResponse`
- [x] `GET /api/cart`: devuelve items + totales calculados
- [x] `POST /api/cart/items`: agregar producto (merge si ya existe)
- [x] `PUT /api/cart/items/{id}`: actualizar cantidad
- [x] `DELETE /api/cart/items/{id}`: eliminar item
- [x] Sincronización carrito: endpoint `POST /api/cart/sync` (localStorage → DB al hacer login)
- [x] Schemas Order: `CheckoutRequest`, `OrderResponse`, `OrderDetail`
- [x] `POST /api/orders/checkout`: validar stock, crear orden, descontar inventario, respuesta con order_id
- [x] `GET /api/orders`: historial del usuario autenticado
- [x] `GET /api/orders/{id}`: detalle con items

### Frontend
- [x] `js/cart.js`: CRUD carrito con localStorage (visitante) y API (autenticado)
- [x] Side drawer carrito: animación slide-in, lista de items, subtotal, botón checkout
- [x] `cart.html`: página completa del carrito con resumen de precios
- [x] `checkout.html`: formulario dirección + selección pago + resumen final
- [x] `js/pages/checkout.js`: validación formulario, POST a API, redirect a confirmación
- [x] Página de confirmación de pedido con número de orden y animación de éxito

---

## FASE 5 — Auth Frontend y Perfil (Día 9)

- [x] `login.html`: tabs Login / Registro con diseño metálico premium
- [x] `js/auth.js`: login, registro, almacenamiento de tokens, refresh automático, logout
- [x] Navbar dinámica: mostrar usuario / botón login según estado de auth
- [x] `orders.html`: historial de órdenes del cliente con estados visuales (badges de color)
- [x] Redirect guards: proteger páginas de checkout y orders si no está autenticado
- [x] `js/pages/forgot-password.js` + formulario recuperación de contraseña

---

## FASE 6 — Panel Admin (Días 10-11)

### Backend
- [x] `GET /api/admin/dashboard`: total ventas hoy, pedidos pendientes, productos con stock < 5
- [x] `GET /api/admin/orders`: todos los pedidos con paginación y filtro por estado
- [x] `PATCH /api/admin/orders/{id}/status`: cambiar estado del pedido

### Frontend Admin
- [x] `admin/dashboard.html`: cards métricas + gráfica ventas últimos 7 días (Chart.js o CSS puro)
- [x] `admin/products.html`: tabla de productos + modal crear/editar + confirmación eliminar
- [x] `js/admin/products.js`: CRUD completo con validaciones inline
- [x] `admin/orders.html`: tabla de pedidos + filtros por estado + selector de cambio de estado
- [x] `js/admin/orders.js`: Lógica de listado, paginación y cambio de estado
- [x] Guard de ruta: solo accesible con rol `admin`

---

## FASE 7 — Email y Pulido (Día 12)

- [x] Configurar FastAPI-Mail con template Jinja2
- [x] Template HTML de confirmación de pedido (estilo metálico)
- [x] Trigger de email al crear orden exitosamente
- [x] Implementar rate limiting en endpoint de login (slowapi)
- [x] Revisar y ajustar responsive en todos los breakpoints (375, 768, 1280px)
- [x] Añadir favicon metálico (SVG inline)
- [x] Metatags SEO básicos en todas las páginas
- [x] Revisar accesibilidad: contraste de colores, labels en forms, aria-labels

---

## FASE 8 — Tests y Deploy (Día 13-14)

### Tests
- [x] `tests/test_auth.py`: register, login, refresh, rutas protegidas
- [x] `tests/test_products.py`: CRUD, filtros, paginación
- [x] `tests/test_cart.py`: agregar, actualizar, eliminar, sync
- [x] `tests/test_orders.py`: checkout con stock suficiente, checkout sin stock
- [x] `tests/test_admin.py`: acceso con y sin rol admin
- [x] Configurar `pytest` con base de datos SQLite en memoria para tests
- [x] CI básico: `ruff check` + `pytest` en GitHub Actions

### Deploy (opcional)
- [x] Configurar variables de entorno para producción
- [x] Dockerfile producción con Gunicorn + Uvicorn workers
- [x] Configurar CORS para dominio de producción
- [x] Servir frontend como archivos estáticos desde FastAPI (`StaticFiles`)
- [x] Documentar proceso de deploy en `README.md`

---

## Backlog (v2)

- [ ] Subida real de imágenes (AWS S3 o Cloudflare R2)
- [ ] Integración con Stripe para pagos reales
- [ ] Sistema de reseñas y ratings por producto
- [ ] Wishlist / lista de deseos
- [ ] Cupones de descuento
- [ ] Notificaciones en tiempo real (WebSockets) para admin
- [ ] PWA con Service Worker para uso offline
- [ ] Internacionalización (ES/EN)
