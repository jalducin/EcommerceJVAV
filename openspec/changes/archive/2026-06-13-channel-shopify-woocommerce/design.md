## Context

Primeros conectores reales sobre el núcleo del Sprint 1. Shopify (Admin API) y WooCommerce (REST API) son
REST, bien documentados y con sandbox gratis (dev store / instalación local), ideales para validar el
framework de adapters end-to-end antes de marketplaces y POS.

## Goals / Non-Goals

**Goals:**
- Dos adapters que implementan la interfaz del framework con capacidades catálogo/inventario/pedidos/fulfillment.
- Publicación de catálogo e inventario canónicos hacia cada tienda; ingesta de pedidos al hub unificado.
- Webhooks validados (HMAC Shopify; firma Woo) + reconciliación por pull; todo idempotente.

**Non-Goals:**
- Multi-store masivo (varias tiendas por proveedor se soporta por configuración, pero el alcance de prueba
  es 1 dev store + 1 Woo local).
- Funciones avanzadas de cada plataforma (descuentos, metafields) más allá de catálogo/inventario/pedidos.

## Decisions

### Decisión 1: Reusar el sync-engine del Sprint 1 (no lógica ad-hoc)
Toda publicación y propagación pasa por EventBridge/SQS con idempotencia y rate limiting; los adapters solo
traducen canónico↔proveedor. Alternativa (llamadas síncronas directas) descartada por rate limits y acoplamiento.

### Decisión 2: Webhooks con verificación por proveedor + pull de respaldo
Shopify firma con HMAC-SHA256 (header `X-Shopify-Hmac-Sha256`); WooCommerce firma con secret configurable.
La verificación vive en cada adapter. Se añade reconciliación por pull (programada) por si se pierde un webhook.

### Decisión 3: Rate limiting específico
Shopify (límite por leaky bucket / cost de GraphQL o REST call limit) y WooCommerce (según hosting). El
rate limiter por proveedor del Sprint 1 se configura por adapter.

## Risks / Trade-offs

- **Pérdida de webhooks** → reconciliación por pull periódica como red de seguridad.
- **Diferencias de modelo (variantes, impuestos)** → el mapeo canónico↔proveedor se prueba con casos reales.
- **Rate limits dispares** → configuración de rate limiter por adapter; difiere, no descarta.

## Migration Plan

1. Adapter Shopify: auth, catálogo/inventario push, webhook `orders/create` + pull, fulfillment.
2. Adapter WooCommerce: auth, catálogo/inventario push, webhook de pedidos + pull, fulfillment.
3. Pruebas con dev store de Shopify y WooCommerce local; verificar anti-sobreventa con ambos canales activos.

## Open Questions

- ¿Shopify vía REST Admin API o GraphQL Admin API? (REST para empezar; GraphQL si el costo/volumen lo exige.)
- ¿Frecuencia de la reconciliación por pull por tienda?
