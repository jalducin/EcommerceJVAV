# Proposal: Gestión de categorías e imágenes de producto en el panel admin

## Why

Hoy el panel admin solo permite **elegir** una categoría de un selector de solo lectura (poblado desde
`GET /api/config`) y registrar **una sola imagen por URL** escrita a mano. No hay forma de **crear o
eliminar categorías** ni de **subir archivos de imagen** ni de gestionar **varias imágenes** por producto.
Eso obliga a editar la configuración fuera de la app y a hospedar las imágenes en otro lado, lo que rompe
la promesa de un panel autosuficiente y business-agnostic.

Este cambio cierra esa brecha: el administrador gestiona las categorías de la tienda y sube/ordena/elimina
las imágenes de cada producto desde el propio panel, con las imágenes almacenadas en el bucket existente
(servidas por el CloudFront ya desplegado), sin infraestructura nueva.

## What Changes

- **Categorías (admin):** endpoints admin para listar, agregar y eliminar categorías de la tienda
  (persisten en `store-config.categories`). No se puede eliminar una categoría en uso por productos activos.
- **Subida de imágenes (admin):** endpoint que devuelve una **URL prefirmada (PUT)** a S3 bajo el prefijo
  `media/`; el navegador sube el archivo directo a S3 y guarda la URL pública (CloudFront) en el producto.
- **Múltiples imágenes por producto:** la UI admin gestiona una galería (agregar por subida o URL, quitar,
  reordenar; la primera es la principal) y envía `images: list[str]` en `POST/PUT /api/products`.
- **Infra (tier-0):** se agrega CORS al bucket de frontend para PUT prefirmado y permiso `s3:PutObject`
  de mínimo privilegio al Lambda sobre `media/*`. Sin bucket ni distribución nuevos.

## Impact

- **Tipos de usuario afectados:** administrador (gestión de catálogo) y operador/DevOps (infra S3/IAM).
- **Specs:** `admin-product-management` (categorías + galería), `admin-media-uploads` (nueva: presign),
  `static-frontend-cdn` (prefijo `media/` + CORS).
- **Código:** `backend/routers/admin.py` (categorías), nuevo router/servicio de uploads, `catalog.py`
  (validación), `frontend/admin/products.html` + `js/admin/products.js`, `template.yaml` (CORS + IAM).
- **Compatibilidad:** aditivo. Los productos existentes con una sola imagen siguen funcionando.
