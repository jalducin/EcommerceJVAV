## 0. Preparación

- [x] 0.1 Rama de trabajo y revisión de los archivos afectados

## 1. Marca y storefront

- [x] 1.1 Renderizar marca desde /api/config (data-store-name); retirar copy de vertical fijo
- [x] 1.2 Rebrand por defecto a "JV Market" (UI, seed, título OpenAPI)
- [x] 1.3 Catálogo demo: 12 productos en 3 categorías con imágenes en /img/products

## 2. Panel admin

- [x] 2.1 dashboard.html: agregar variables.css (faltaba) y quitar utils.js inexistente
- [x] 2.2 guard: sesión no-admin redirige a login con next

## 3. Swagger

- [x] 3.1 FastAPI root_path al stage para servir openapi.json bajo /dev

## 4. Verificación (OBLIGATORIO — EL AGENTE EJECUTA)

- [x] 4.1 ruff + pytest en verde (75 tests)
- [x] 4.2 Verificación en vivo: storefront, panel, /api/docs (200), /api/config (JV Market)
