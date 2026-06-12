---
description: Estándares de frontend de MetalShop (HTML5 / CSS3 / JS Vanilla, paleta metálica, responsive mobile-first).
alwaysApply: true
---

# Estándares de frontend — MetalShop

> Complementa `base-standards.md` y `documentation-standards.md`. Aplica a todo cambio que toque
> `frontend/` (HTML, CSS, JS).

## 1. Stack (no negociable)

- HTML5 + CSS3 + JavaScript Vanilla. **Sin frameworks JS** (React, Vue, Angular).
- **Sin frameworks CSS** (Bootstrap, Tailwind). Usar CSS Custom Properties.
- HTTP con Fetch API (nativo). Fuentes: Rajdhani (títulos) + Inter (cuerpo) vía Google Fonts.
- Íconos: Lucide Icons vía CDN. Sin build step.

## 2. Paleta de colores metálica

Usar siempre estas variables CSS (definidas en `frontend/css/variables.css`); **nunca hardcodear colores**:

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

## 3. Reglas de CSS

- **Mobile-first**, breakpoints: 375px, 768px, 1280px.
- Usar las variables de `css/variables.css`; no duplicar tokens.
- Transiciones de 200-300ms ease.
- **Nunca `!important`.**

## 4. Reglas de JavaScript

- Fetch API para todas las llamadas HTTP, vía el wrapper `js/api.js` (base URL, headers de auth, errores).
- Siempre manejar errores con try/catch.
- Tokens JWT en `localStorage` con refresh automático (ver `js/auth.js`).
- Debounce de 300ms en búsquedas.

## 5. Estructura

```
frontend/
  *.html              # index, product, cart, checkout, login, orders, order-confirm, forgot-password
  admin/              # dashboard.html, products.html, orders.html
  css/                # variables.css, base.css, components.css, admin.css
  js/                 # api.js, cart.js, auth.js
    pages/            # catalog, product, checkout, login, orders, forgot-password
    admin/            # dashboard, products, orders
```

## 6. Calidad

- Responsive verificado en los tres breakpoints (375/768/1280px).
- Accesibilidad: contraste suficiente, labels en formularios, `aria-label` donde aplique.
- Metatags SEO básicos en cada página.

## 7. Verificación manual (Step N+2 de la regla de tasks)

Para cambios de UI, el agente ejecuta el flujo de usuario afectado (manual o E2E) y verifica el
resultado en al menos un breakpoint móvil y uno desktop, cubriendo estados de error visibles.
