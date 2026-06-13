## Context

Canales sociales y Google Shopping sobre el núcleo del Sprint 1. El patrón dominante es **feed de
productos** (catálogo canónico → catálogo del canal), con ingesta de pedidos donde exista checkout nativo
(Meta, TikTok). Google Merchant es feed puro (sin pedidos). Todos requieren apps/cuentas de desarrollador
con procesos de revisión propios.

## Goals / Non-Goals

**Goals:**
- Adapters de Meta, TikTok Shop y Google Merchant sobre el framework.
- Publicación de catálogo/inventario como feeds; ingesta de pedidos en Meta/TikTok donde aplique.

**Non-Goals:**
- Gestión de campañas/ads; el alcance es catálogo/feed (+ pedidos donde el canal lo permita).
- Contenido orgánico/posts; solo comercio.

## Decisions

### Decisión 1: Feed-first, pedidos donde aplique
Google Merchant: solo feed (Content API). Meta: feed de catálogo y pedidos si hay checkout nativo. TikTok
Shop: catálogo + inventario + pedidos. Cada adapter declara solo las capacidades que el canal soporta.

### Decisión 2: Publicación de feeds por job programado + por evento
Los feeds se regeneran ante cambios del catálogo (evento) y/o de forma programada (EventBridge Scheduler)
para refrescos completos. Errores por producto se reportan sin abortar el lote (observabilidad del Sprint 1).

### Decisión 3: Auth OAuth/cuenta de servicio por proveedor
Meta (Graph API OAuth), TikTok Shop (OAuth), Google (cuenta de servicio/OAuth). Tokens/credenciales en el
vault con refresh del framework.

## Risks / Trade-offs

- **Revisión de apps (Meta/TikTok/Google)** → tratar como prerrequisito de ejecución; specs no se bloquean.
- **Calidad de datos para feeds** (GTIN, imágenes, categorías) → validar y reportar por producto.
- **Diferencias de modelo de pedido social** → mapear solo lo soportado por cada canal.

## Migration Plan

1. Google Merchant: feed de catálogo vía Content API (más simple, feed puro).
2. Meta Commerce: feed de catálogo + pedidos donde aplique.
3. TikTok Shop: catálogo/inventario + pedidos.

## Open Questions

- ¿Generación de feed por API directa vs archivo de feed (XML/TSV) por canal?
- ¿Frecuencia de refresco completo del feed por canal?
