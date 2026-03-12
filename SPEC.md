# SPEC.md — Especificación Funcional
## MetalShop · Ecommerce en Python con UI Metálica

---

## 1. Visión del Producto

**MetalShop** es una tienda en línea construida con Python (FastAPI) y un frontend estático con estética metálica premium (plata, oro, acero, cobre). Orientada a venta de productos genéricos con una experiencia visual de alto impacto.

---

## 2. Usuarios

| Rol | Descripción |
|---|---|
| **Visitante** | Navega el catálogo sin cuenta |
| **Cliente** | Registrado, puede comprar y ver historial |
| **Admin** | Gestiona productos, pedidos e inventario |

---

## 3. Módulos Funcionales

### 3.1 Catálogo
- Listado de productos con imagen, nombre, precio y badge de stock
- Filtros por categoría, precio y disponibilidad
- Búsqueda en tiempo real (debounce 300ms)
- Vista detalle de producto con galería de imágenes

### 3.2 Carrito de Compras
- Agregar / eliminar / modificar cantidad
- Persistencia en localStorage (visitante) y base de datos (cliente)
- Resumen de precios con subtotal, envío e impuesto
- Carrito deslizante (side drawer) sin salir de la página

### 3.3 Autenticación
- Registro con email + contraseña
- Login con JWT (access token 30min + refresh token 7 días)
- Recuperación de contraseña por email

### 3.4 Checkout
- Formulario de dirección de envío
- Selección de método de pago (tarjeta simulada / efectivo)
- Confirmación de pedido con número de orden
- Email de confirmación automático

### 3.5 Panel Admin
- Dashboard con métricas: ventas del día, pedidos pendientes, productos agotados
- CRUD de productos (nombre, descripción, precio, stock, imágenes, categoría)
- Listado de pedidos con cambio de estado (pendiente → enviado → entregado)

### 3.6 Historial de Pedidos (Cliente)
- Lista de órdenes pasadas con estado visual
- Detalle de cada orden

---

## 4. Diseño Visual

### Paleta Metálica
| Token | Color | Uso |
|---|---|---|
| `--silver` | `#C0C0C0` | Fondos secundarios, bordes |
| `--gold` | `#D4AF37` | CTAs principales, highlights |
| `--steel` | `#4A5568` | Textura base, navbar |
| `--copper` | `#B87333` | Acentos, badges |
| `--chrome` | `#E8E8E8` | Cards, superficies |
| `--dark-metal` | `#1A1A2E` | Fondo principal |

### Efectos
- Gradientes metálicos en botones y headers
- Sombras con brillo (`box-shadow` con color dorado/plateado)
- Transiciones suaves 200-300ms
- Tipografía: `Rajdhani` (títulos) + `Inter` (cuerpo)
- Cards con efecto hover de elevación y brillo

---

## 5. Restricciones

- Sin pagos reales en v1 (modo simulado)
- Máximo 1000 productos en catálogo inicial
- Imágenes: máximo 5MB por producto, formatos JPG/PNG/WebP
- Compatible con Chrome, Firefox, Safari (últimas 2 versiones)
- Responsive: mobile-first (breakpoints 375px, 768px, 1280px)
