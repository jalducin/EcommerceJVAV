"""App FastAPI serverless de MetalShop (Lambdalith).

Solo expone `/api/*`; el frontend estático se sirve desde S3/CloudFront. El handler
Mangum adapta la app a AWS Lambda + API Gateway.

Durante la migración conviven routers ya migrados a DynamoDB (store, catalog).
Los routers legacy (auth/cart/orders/admin sobre SQLAlchemy) se irán portando e
integrando aquí, y el monolito se decomisiona al final del cambio.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from backend.config import settings
from backend.routers import accounts as accounts_router
from backend.routers import cart_dynamo as cart_router
from backend.routers import catalog as catalog_router
from backend.routers import orders_dynamo as orders_router
from backend.routers import store as store_router

app = FastAPI(
    title="MetalShop API (serverless)",
    description="Plataforma ecommerce configurable sobre AWS serverless",
    version="0.2.0",
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


@app.get("/api/health", tags=["health"])
def health() -> dict:
    return {"status": "ok", "env": settings.ENVIRONMENT}


# Handler para AWS Lambda (API Gateway).
handler = Mangum(app)
