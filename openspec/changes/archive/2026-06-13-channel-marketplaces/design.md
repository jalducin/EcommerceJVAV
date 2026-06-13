## Context

Marketplaces sobre el núcleo del Sprint 1. Amazon SP-API (global) y MercadoLibre (LATAM) aportan volumen
con APIs más complejas: OAuth/LWA, rate limits estrictos, modelos de listing/fulfillment propios y
notificaciones asíncronas. MercadoLibre es practicable con test users gratis; Amazon SP-API es deuda
técnica diferida (requiere cuenta de vendedor + aprobación).

## Goals / Non-Goals

**Goals:**
- Adapters de Amazon y MercadoLibre con capacidades catálogo/inventario/pedidos sobre el framework.
- Publicación de listings/inventario canónicos; ingesta de pedidos al hub; reconciliación periódica.

**Non-Goals:**
- Logística avanzada (FBA fulfillment completo, etiquetas de envío) más allá de inventario y pedidos.
- Catálogo de Amazon vía matching ASIN complejo; alcance: crear/actualizar listings propios.

## Decisions

### Decisión 1: Auth por proveedor con refresh en el vault
Amazon: LWA (refresh token → access token). MercadoLibre: OAuth 2.0 (refresh token). El refresh vive en el
framework (Sprint 1); cada adapter solo declara su flujo.

### Decisión 2: Notificaciones + pull de respaldo
Amazon expone notificaciones (vía EventBridge/SQS de Amazon); MercadoLibre vía topics (webhooks). Ambas se
complementan con pull de la Orders API para no perder eventos. Ingesta idempotente por mapeo de IDs.

### Decisión 3: Rate limiting estricto por adapter
SP-API tiene cuotas por operación; MercadoLibre limita por app/usuario. El rate limiter del Sprint 1 se
configura con parámetros propios por adapter; ante throttling, difiere y reintenta.

### Decisión 4: Amazon como deuda técnica diferida
Se especa y diseña completo, pero la implementación/verificación queda diferida hasta tener cuenta de
vendedor profesional y aprobación de la app (ver política tier 0 del roadmap). MercadoLibre se implementa
con test users.

## Risks / Trade-offs

- **Aprobación/cuenta de Amazon** → diferir como deuda técnica; no bloquea MercadoLibre.
- **Rate limits estrictos** → backoff + diferir; nunca descartar trabajos.
- **Modelos de listing dispares** → mapeo canónico↔proveedor probado con casos reales (test users MeLi).

## Migration Plan

1. MercadoLibre (ejecutable): OAuth, publicaciones/inventario, notificaciones + pull, fulfillment básico.
2. Amazon (diferido): LWA, feeds de listings/inventario, notificaciones + Orders API — implementar al tener acceso.

## Open Questions

- ¿Estrategia de matching/creación de listings en Amazon (productos propios vs catálogo existente)?
- ¿Frecuencia de pull de respaldo por marketplace dado el rate limit?
