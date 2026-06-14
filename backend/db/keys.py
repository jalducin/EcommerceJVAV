"""Helpers de claves para el diseño single-table.

Centraliza la construcción de PK/SK y de los atributos de GSI por entidad, para que
los repositorios no esparzan literales de claves.
"""

from __future__ import annotations

# --- Producto -------------------------------------------------------------
# PK = PRODUCT#<id>, SK = PRODUCT ; GSI2 = CAT#<categoria> / PRODUCT#<id>


def product_pk(product_id: str) -> str:
    return f"PRODUCT#{product_id}"


PRODUCT_SK = "PRODUCT"


def product_gsi2(category: str, product_id: str) -> dict:
    return {"GSI2PK": f"CAT#{category}", "GSI2SK": f"PRODUCT#{product_id}"}


# Inventario por variante (fuente de verdad del stock):
# PK = PRODUCT#<id>, SK = STOCK#<sku>  ("-" si el producto no tiene variantes)


def stock_sk(sku: str) -> str:
    return f"STOCK#{sku}"


STOCK_SK_PREFIX = "STOCK#"


# --- Usuario --------------------------------------------------------------
# PK = USER#<id>, SK = PROFILE ; GSI1 = EMAIL#<email> / USER


def user_pk(user_id: str) -> str:
    return f"USER#{user_id}"


USER_SK = "PROFILE"


def user_gsi1(email: str) -> dict:
    return {"GSI1PK": f"EMAIL#{email.lower()}", "GSI1SK": "USER"}


# --- Carrito --------------------------------------------------------------
# PK = USER#<id>, SK = CART#<product_id>#<variant_key>


def cart_sk(product_id: str, variant_key: str = "-") -> str:
    return f"CART#{product_id}#{variant_key}"


CART_SK_PREFIX = "CART#"


# --- Pedido ---------------------------------------------------------------
# PK = USER#<id>, SK = ORDER#<created_at>#<id>
# GSI3 = ORDERS / <status>#<created_at>#<id>


def order_sk(created_at: str, order_id: str) -> str:
    return f"ORDER#{created_at}#{order_id}"


ORDER_SK_PREFIX = "ORDER#"


def order_gsi3(status: str, created_at: str, order_id: str) -> dict:
    return {"GSI3PK": "ORDERS", "GSI3SK": f"{status}#{created_at}#{order_id}"}


# --- Configuración de tienda ---------------------------------------------
# PK = CONFIG, SK = STORE

CONFIG_PK = "CONFIG"
CONFIG_SK = "STORE"


# --- Lista de deseos ------------------------------------------------------
# PK = USER#<id>, SK = WISH#<product_id>


def wish_sk(product_id: str) -> str:
    return f"WISH#{product_id}"


WISH_SK_PREFIX = "WISH#"


# --- Mapeo de IDs externo <-> canónico (integraciones) -------------------
# externo -> canónico:  PK = MAP#<connector>#<entity>, SK = EXT#<external_id>
# canónico -> externo:  PK = ENTITY#<entity>#<canonical_id>, SK = MAPC#<connector>


def map_ext_pk(connector: str, entity: str) -> str:
    return f"MAP#{connector}#{entity}"


def map_ext_sk(external_id: str) -> str:
    return f"EXT#{external_id}"


def map_canon_pk(entity: str, canonical_id: str) -> str:
    return f"ENTITY#{entity}#{canonical_id}"


def map_canon_sk(connector: str) -> str:
    return f"MAPC#{connector}"
