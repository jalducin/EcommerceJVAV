"""App FastAPI serverless de MetalShop (Lambdalith).

Solo expone `/api/*`; el frontend estático se sirve desde S3/CloudFront. El handler
Mangum adapta la app a AWS Lambda + API Gateway.

Durante la migración conviven routers ya migrados a DynamoDB (store, catalog).
Los routers legacy (auth/cart/orders/admin sobre SQLAlchemy) se irán portando e
integrando aquí, y el monolito se decomisiona al final del cambio.
"""

from __future__ import annotations

import secrets

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from mangum import Mangum

from backend.config import settings
from backend.routers import accounts as accounts_router
from backend.routers import admin as admin_router
from backend.routers import cart_dynamo as cart_router
from backend.routers import catalog as catalog_router
from backend.routers import orders_dynamo as orders_router
from backend.routers import store as store_router

OPENAPI_TAGS = [
    {"name": "health", "description": "Estado del servicio."},
    {"name": "config", "description": "Configuración de tienda business-agnostic."},
    {"name": "auth", "description": "Registro, login (JWT), refresh y perfil."},
    {"name": "products", "description": "Catálogo: filtros, detalle y CRUD admin."},
    {"name": "cart", "description": "Carrito del usuario: items y sincronización."},
    {"name": "orders", "description": "Checkout transaccional e historial."},
    {"name": "admin", "description": "Panel admin (requiere rol admin)."},
]

# En Lambda+API Gateway el stage (p. ej. /dev) va en la URL pública. root_path se
# lo indica a FastAPI para que Swagger UI pida el openapi.json con ese prefijo.
# Local (ENVIRONMENT=development) no usa stage -> root_path vacío.
_STAGE = settings.ENVIRONMENT if settings.ENVIRONMENT in ("dev", "prod") else ""

# Docs deshabilitados de fábrica: se montan rutas propias protegidas con Basic auth
# (solo si hay DOCS_PASSWORD). Seguro por defecto.
app = FastAPI(
    title="JV Market API",
    description=(
        "Plataforma ecommerce multicanal sobre AWS serverless (Lambda + API Gateway + "
        "DynamoDB). Documentación protegida en `/api/docs`."
    ),
    version="0.2.0",
    openapi_tags=OPENAPI_TAGS,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    root_path=f"/{_STAGE}" if _STAGE else "",
)

# ── Documentación protegida (candado) ─────────────────────────────────────────
_docs_basic = HTTPBasic(auto_error=True)


def _check_docs_auth(creds: HTTPBasicCredentials = Depends(_docs_basic)) -> str:
    user_ok = secrets.compare_digest(creds.username, settings.DOCS_USER)
    pass_ok = secrets.compare_digest(creds.password, settings.DOCS_PASSWORD)
    if not (user_ok and pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de documentación inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return creds.username


if settings.DOCS_PASSWORD:  # docs habilitados solo si hay contraseña configurada

    @app.get("/api/openapi.json", include_in_schema=False)
    def _openapi(_: str = Depends(_check_docs_auth)) -> dict:
        return app.openapi()

    @app.get("/api/docs", include_in_schema=False)
    def _docs(request: Request, _: str = Depends(_check_docs_auth)):
        root = request.scope.get("root_path", "")
        return get_swagger_ui_html(
            openapi_url=f"{root}/api/openapi.json", title="JV Market API — Docs"
        )

    @app.get("/api/redoc", include_in_schema=False)
    def _redoc(request: Request, _: str = Depends(_check_docs_auth)):
        root = request.scope.get("root_path", "")
        return get_redoc_html(
            openapi_url=f"{root}/api/openapi.json", title="JV Market API — Docs"
        )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"]
    if settings.ENVIRONMENT == "development"
    else [settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(store_router.router)
app.include_router(accounts_router.router)
app.include_router(catalog_router.router)
app.include_router(cart_router.router)
app.include_router(orders_router.router)
app.include_router(admin_router.router)


@app.get("/api/health", tags=["health"])
def health() -> dict:
    return {"status": "ok", "env": settings.ENVIRONMENT}


# Handler para AWS Lambda (API Gateway).
# El stage de HTTP API (p. ej. /dev) va en el path; se le indica a Mangum para
# que lo recorte y FastAPI vea /api/... (el stage coincide con ENVIRONMENT).
handler = Mangum(app, api_gateway_base_path=f"/{settings.ENVIRONMENT}")
