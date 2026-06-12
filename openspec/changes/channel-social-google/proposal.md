## Why

El comercio social (Meta, TikTok) y Google Shopping amplían alcance con catálogos/feeds y, en algunos
casos, pedidos. El patrón dominante aquí es **feed de productos** (catálogo canónico → feed del canal),
con ingesta de pedidos donde la plataforma lo permita. Sprint 4 del roadmap.

## What Changes

- **Adapter de Meta Commerce** (Facebook/Instagram Shop): catálogo/feed de productos y, donde aplique,
  pedidos.
- **Adapter de TikTok Shop**: catálogo, inventario y pedidos del canal social.
- **Adapter de Google Merchant Center**: feed de productos para Google Shopping (Content API).
- Publicación de catálogo/inventario canónico como feeds y, donde exista, ingesta de pedidos al hub
  unificado.

## Capabilities

### New Capabilities
- `meta-commerce-connector`: catálogo/feed (y pedidos donde aplique) de Facebook/Instagram Shop.
- `tiktok-shop-connector`: catálogo, inventario y pedidos de TikTok Shop.
- `google-merchant-connector`: feed de productos para Google Shopping (Content API for Shopping).

### Modified Capabilities
<!-- Usa las capabilities del Sprint 1. -->

## Impact

- **Backend**: `backend/integrations/meta/`, `tiktok/`, `google_merchant/` (auth OAuth, generación de
  feeds, mapeo de catálogo).
- **Infra**: secretos OAuth; jobs programados de publicación de feeds; webhooks de pedidos donde aplique.
- **Tests**: cuentas/sandbox de cada plataforma; validación del feed generado.
- **Docs**: sección por conector; diferencias feed vs pedidos.
- **Dependencia**: requiere `integration-platform-core` (Sprint 1).
- **Acceso**: requieren apps/cuentas de desarrollador (Meta, TikTok, Google) con sus procesos de revisión.
