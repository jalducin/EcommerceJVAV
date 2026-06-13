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
    name="JV Market",
    categories=["tenis", "ropa", "accesorios"],
    currency="MXN",
    locale="es-MX",
    tax_rate=0.16,
    shipping_flat=99.0,
    free_shipping_threshold=1500.0,
)

DEFAULT_ADMIN = UserCreate(
    email="admin@metalshop.mx", password="Admin123!", full_name="Admin JV Market"
)

# Cliente demo para probar el flujo de compra (rol client).
DEFAULT_CLIENT = UserCreate(
    email="cliente@metalshop.mx", password="Cliente123!", full_name="Cliente Demo"
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


def _p(idx, **kw):
    """Helper para fijar created_at incremental de forma legible."""
    kw["created_at"] = f"2026-01-{idx:02d}T00:00:00+00:00"
    return Product(**kw)


DEFAULT_PRODUCTS = [
    # ── Tenis ──────────────────────────────────────────────────────────────
    _p(
        1,
        id="tenis-runner-metal",
        name="Tenis Runner Metal",
        category="tenis",
        description="Sneakers de running con acabado metálico premium.",
        price=1899.0,
        images=["/img/products/runner.jpg", "/img/products/runner2.jpg"],
        variants=_tallas("RUNNER", ["41", "42", "43", "44"], stock=6),
    ),
    _p(
        2,
        id="tenis-trail-chrome",
        name="Tenis Trail Chrome",
        category="tenis",
        description="Sneakers todo terreno con suela reforzada.",
        price=2499.0,
        images=["/img/products/trail.jpg"],
        variants=_tallas("TRAIL", ["40", "41", "42", "43"], stock=4, color="acero"),
    ),
    _p(
        3,
        id="tenis-court-silver",
        name="Tenis Court Silver",
        category="tenis",
        description="Sneakers clásicos de cancha en plata.",
        price=1599.0,
        images=["/img/products/court.jpg"],
        variants=_tallas(
            "COURT", ["40", "41", "42", "43", "44"], stock=8, color="plata"
        ),
    ),
    _p(
        4,
        id="tenis-boost-gold",
        name="Tenis Boost Gold",
        category="tenis",
        description="Sneakers de alto rendimiento con detalle dorado.",
        price=2899.0,
        images=["/img/products/boost.jpg"],
        variants=_tallas("BOOST", ["41", "42", "43"], stock=3, color="oro"),
    ),
    # ── Ropa ───────────────────────────────────────────────────────────────
    _p(
        5,
        id="hoodie-oversize-gold",
        name="Hoodie Oversize Gold",
        category="ropa",
        description="Sudadera oversize con detalles dorados.",
        price=899.0,
        images=["/img/products/hoodie.jpg", "/img/products/hoodie2.jpg"],
        variants=_tallas("HOODIE", ["S", "M", "L", "XL"], stock=10),
    ),
    _p(
        6,
        id="playera-tech-silver",
        name="Playera Tech Silver",
        category="ropa",
        description="Playera técnica transpirable con estampado plateado.",
        price=499.0,
        images=["/img/products/tee.jpg"],
        variants=_tallas("TEE", ["S", "M", "L"], stock=15),
    ),
    _p(
        7,
        id="joggers-steel",
        name="Joggers Steel",
        category="ropa",
        description="Pantalón jogger de corte urbano color acero.",
        price=799.0,
        images=["/img/products/joggers.jpg"],
        variants=_tallas("JOG", ["S", "M", "L", "XL"], stock=7, color="acero"),
    ),
    _p(
        8,
        id="chamarra-chrome",
        name="Chamarra Chrome",
        category="ropa",
        description="Chamarra ligera con acabado metálico.",
        price=1799.0,
        images=["/img/products/jacket.jpg"],
        variants=_tallas("JACKET", ["S", "M", "L"], stock=5, color="cromo"),
    ),
    # ── Accesorios ─────────────────────────────────────────────────────────
    _p(
        9,
        id="gorra-copper",
        name="Gorra Copper",
        category="accesorios",
        description="Gorra snapback con logo cobre.",
        price=349.0,
        images=["/img/products/cap.jpg"],
        stock=20,
    ),
    _p(
        10,
        id="mochila-urban",
        name="Mochila Urban",
        category="accesorios",
        description="Mochila urbana resistente al agua.",
        price=1099.0,
        images=["/img/products/backpack.jpg"],
        stock=12,
    ),
    _p(
        11,
        id="calcetines-metal-pack",
        name="Calcetines Metal (pack 3)",
        category="accesorios",
        description="Pack de 3 pares de calcetines deportivos.",
        price=199.0,
        images=["/img/products/socks.jpg"],
        stock=40,
    ),
    _p(
        12,
        id="lentes-solar-gold",
        name="Lentes Solar Gold",
        category="accesorios",
        description="Lentes de sol con armazón dorado y filtro UV.",
        price=649.0,
        images=["/img/products/sunglasses.jpg"],
        stock=9,
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

    # Cliente demo (rol client) idempotente.
    if not user_repo.get_user_by_email(str(DEFAULT_CLIENT.email)):
        user_repo.create_user(DEFAULT_CLIENT, role="client")

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
