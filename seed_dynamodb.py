"""Cargador idempotente de datos demo en DynamoDB (reemplaza seed_products.py).

Dataset por defecto: streetwear y tenis (ropa + sneakers). El dataset es
intercambiable: pásalo a `seed()` para sembrar otro vertical sin tocar código.

Uso:
    poetry run python seed_dynamodb.py          # crea tabla (si falta) + siembra demo
    poetry run python seed_dynamodb.py --no-create-table
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone

from backend.db.dynamo import create_table
from backend.repositories import product_repo, store_repo, user_repo
from backend.schemas.account import UserCreate
from backend.schemas.catalog import Product, Variant
from backend.schemas.store import StoreConfig

# --- Dataset demo por defecto: ropa y tenis -------------------------------

DEFAULT_CONFIG = StoreConfig(
    name="MetalShop",
    categories=["tenis", "ropa", "accesorios"],
    currency="MXN",
    locale="es-MX",
    tax_rate=0.16,
    shipping_flat=99.0,
    free_shipping_threshold=1500.0,
)

DEFAULT_ADMIN = UserCreate(
    email="admin@metalshop.mx", password="Admin123!", full_name="Admin MetalShop"
)


def _tallas(
    prefix: str, tallas: list[str], stock: int, color: str = "negro"
) -> list[Variant]:
    return [
        Variant(
            sku=f"{prefix}-{t}-{color[:3].upper()}",
            attrs={"talla": t, "color": color},
            stock=stock,
        )
        for t in tallas
    ]


DEFAULT_PRODUCTS = [
    Product(
        id="tenis-runner-metal",
        name="Tenis Runner Metal",
        description="Sneakers de running con acabado metálico premium.",
        price=1899.0,
        category="tenis",
        images=["/img/products/runner.jpg", "/img/products/runner2.jpg"],
        variants=_tallas("RUNNER", ["41", "42", "43", "44"], stock=6),
        created_at="2026-01-01T00:00:00+00:00",
    ),
    Product(
        id="tenis-trail-chrome",
        name="Tenis Trail Chrome",
        description="Sneakers todo terreno con suela reforzada.",
        price=2499.0,
        category="tenis",
        images=["/img/products/trail.jpg"],
        variants=_tallas("TRAIL", ["40", "41", "42", "43"], stock=4, color="acero"),
        created_at="2026-01-02T00:00:00+00:00",
    ),
    Product(
        id="hoodie-oversize-gold",
        name="Hoodie Oversize Gold",
        description="Sudadera oversize con detalles dorados.",
        price=899.0,
        category="ropa",
        images=["/img/products/hoodie.jpg", "/img/products/hoodie2.jpg"],
        variants=_tallas("HOODIE", ["S", "M", "L", "XL"], stock=10),
        created_at="2026-01-03T00:00:00+00:00",
    ),
    Product(
        id="playera-tech-silver",
        name="Playera Tech Silver",
        description="Playera técnica transpirable con estampado plateado.",
        price=499.0,
        category="ropa",
        images=["/img/products/tee.jpg"],
        variants=_tallas("TEE", ["S", "M", "L"], stock=15),
        created_at="2026-01-04T00:00:00+00:00",
    ),
    Product(
        id="gorra-copper",
        name="Gorra Copper",
        description="Gorra snapback con logo cobre.",
        price=349.0,
        category="accesorios",
        images=["/img/products/cap.jpg"],
        stock=20,  # sin variantes
        created_at="2026-01-05T00:00:00+00:00",
    ),
]


def seed(
    config: StoreConfig = DEFAULT_CONFIG,
    products: list[Product] | None = None,
    admin: UserCreate | None = DEFAULT_ADMIN,
) -> dict:
    """Siembra config + productos (+ admin) idempotente. Devuelve un resumen."""
    products = DEFAULT_PRODUCTS if products is None else products

    store_repo.put_config(config)
    for product in products:
        product_repo.put_product(product)

    admin_created = False
    if admin is not None and not user_repo.get_user_by_email(str(admin.email)):
        user_repo.create_user(admin, role="admin")
        admin_created = True

    return {
        "config": config.name,
        "products": len(products),
        "admin_created": admin_created,
        "at": datetime.now(timezone.utc).isoformat(),
    }


def main() -> None:
    if "--no-create-table" not in sys.argv:
        create_table()
    summary = seed()
    print(
        f"Sembrado: tienda='{summary['config']}', "
        f"{summary['products']} productos, admin_creado={summary['admin_created']}"
    )


if __name__ == "__main__":
    main()
