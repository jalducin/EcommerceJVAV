## 0. Preparación
- [x] 0.1 Rama feature/secure-api-docs

## 1. Implementación
- [x] 1.1 config: DOCS_USER/DOCS_PASSWORD
- [x] 1.2 app.py: desactivar docs nativos; rutas propias con Basic auth; off si no hay password
- [x] 1.3 template.yaml: parámetro DocsPassword (NoEcho) + env DOCS_PASSWORD

## 2. Pruebas (OBLIGATORIO — EL AGENTE EJECUTA)
- [x] 2.1 401 sin credenciales; 200 con credenciales; 404 si docs deshabilitados
- [x] 2.2 ruff + pytest en verde

## 3. Despliegue y verificación
- [x] 3.1 deploy con DocsPassword; verificar 401 público y 200 con credenciales en vivo

## 4. Documentación
- [x] 4.1 Swagger/OpenAPI y runbook operador actualizados (credenciales de docs)
