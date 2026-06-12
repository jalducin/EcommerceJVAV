# Roadmap — Plataforma de Comercio Multicanal + CRM + POS

> Documento de planificación. Divide la visión (ecommerce → hub de integración multicanal) en **sprints**,
> cada uno mapeado a un **cambio OpenSpec** en `openspec/changes/`. Es la fuente de verdad de la
> secuenciación; cada cambio detalla sus specs con `/opsx:ff` al iniciar su sprint.

## Visión

Convertir MetalShop en una **plataforma de comercio unificada**: un núcleo serverless y configurable que
actúa como **fuente única de verdad** de catálogo, inventario, pedidos y clientes, y que se integra
mediante **conectores** con canales de venta, CRM/ERP y POS. El inventario se sincroniza en todos los
canales para evitar sobreventa; los pedidos de todos los canales se consolidan en un hub unificado.

## Principio rector

**Anti-corruption layer**: cada servicio externo tiene su propio modelo y semántica. El núcleo define un
**modelo canónico** y cada integración es un **adapter** que traduce entre el modelo externo y el canónico.
Nada específico de un proveedor contamina el dominio. Añadir un proveedor = añadir un adapter, sin tocar
el núcleo (alineado con el principio business-agnostic del Sprint 0).

## Nota sobre "tier 0" / aprendizaje

El valor de arquitectura y specs aplica completo. Para **ejecutar** de verdad, no todos los proveedores
son gratuitos: usar sandbox/test donde exista (Shopify dev store, WooCommerce local, Stripe/Square/
Conekta/Clip test mode, HubSpot/Zoho free, MercadoLibre test users, Meta/TikTok/Google sandbox). Requieren
cuenta pagada o aprobación: **Amazon SP-API, NetSuite, Salesforce, Lightspeed** (specear sí; ejecutar,
solo si hay acceso).

## Sprints

### Sprint 0 — Fundación serverless + plataforma configurable ✅ (specced)
- Cambio: `migrate-to-serverless-aws`
- Entrega: runtime serverless (Lambda/API Gateway), DynamoDB single-table, producto con variantes
  genéricas, configuración de tienda, frontend S3/CloudFront, SES, IaC SAM, datos demo.
- **Prerrequisito de todo lo demás.**

### Sprint 1 — Núcleo de integración (`integration-platform-core`)
- Modelo canónico (Producto, Variante, Inventario, Pedido, Cliente, Pago, Fulfillment).
- Connector framework (interfaz de adapter, registro, capacidades, mapeo de IDs externos↔canónicos).
- Vault de credenciales (AWS Secrets Manager) + flujos OAuth y refresh de tokens.
- Ingesta de webhooks (API Gateway → validación de firma → cola).
- Motor de sincronización async (EventBridge + SQS + DLQ), idempotencia, reintentos/backoff,
  rate limiting por proveedor.
- Inventario unificado (fuente única, anti-sobreventa) y hub de pedidos unificado.
- Observabilidad (logs estructurados, métricas, estado de sync, dead-letter).
- **Habilita todos los conectores.** Sin proveedores aún (framework + un conector de referencia mock).

### Sprint 2 — Canales e-commerce REST (`channel-shopify-woocommerce`)
- Shopify Admin API, WooCommerce REST API.
- Sync de catálogo/inventario (push), ingesta de pedidos (webhooks/pull), estados de fulfillment.
- Los más sencillos (REST + sandbox gratis) → primeros conectores reales sobre el framework.

### Sprint 3 — Marketplaces (`channel-marketplaces`)
- Amazon SP-API, MercadoLibre API.
- Listings, inventario, pedidos; OAuth/LWA, particularidades de cada marketplace, rate limits estrictos.

### Sprint 4 — Social commerce + Shopping (`channel-social-google`)
- Meta Commerce (Facebook/Instagram), TikTok Shop, Google Merchant Center.
- Feeds de productos, catálogos, pedidos sociales donde aplique.

### Sprint 5 — CRM / ERP / Inventario (`crm-erp-inventory`)
- Salesforce, HubSpot, Zoho CRM; NetSuite, Odoo (ERP); Cin7/Skubana (inventario multialmacén).
- Sync de clientes/contactos (canónico ↔ CRM) y de inventario/almacenes (ERP/IMS como fuente alterna).

### Sprint 6 — POS y pagos (`pos-payments`)
- Square, Lightspeed (POS retail); Stripe Terminal (pagos presenciales); Clip, Conekta (pagos México).
- Ventas presenciales hacia el hub de pedidos, conciliación de pagos, inventario en tiempo real en tienda.

## Dependencias

```
Sprint 0 (serverless + config)
        │
        ▼
Sprint 1 (núcleo de integración)  ← habilita TODO lo siguiente
        │
        ├──► Sprint 2 (Shopify/Woo)      [canales REST]
        ├──► Sprint 3 (marketplaces)     [Amazon/MeLi]
        ├──► Sprint 4 (social/Google)    [Meta/TikTok/GMC]
        ├──► Sprint 5 (CRM/ERP/IMS)
        └──► Sprint 6 (POS/pagos)
```

Los Sprints 2-6 son **paralelizables** entre sí una vez listo el Sprint 1; se priorizan por disponibilidad
de sandbox y valor.

## Mapa integración → sprint

| Servicio | Categoría | Sprint |
|---|---|---|
| Shopify, WooCommerce | Canal e-commerce | 2 |
| Amazon SP-API, MercadoLibre | Marketplace | 3 |
| Meta Commerce, TikTok Shop, Google Merchant | Social/Shopping | 4 |
| Salesforce, HubSpot, Zoho | CRM | 5 |
| NetSuite, Odoo | ERP | 5 |
| Cin7, Skubana | Inventario multialmacén | 5 |
| Square, Lightspeed | POS retail | 6 |
| Stripe Terminal | Pagos presenciales | 6 |
| Clip, Conekta | Pagos México | 6 |

## Cómo avanzar cada sprint

1. `/opsx:ff <change-name>` (modelo de razonamiento alto) para generar specs → design → tasks del sprint.
2. `/opsx:apply <change-name>` para implementar (Step 0 rama, pruebas, verificación, docs).
3. `/opsx:verify` y `/opsx:archive` al cerrar; el spec archivado puebla `openspec/specs/`.
