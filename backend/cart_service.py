"""Lógica compartida de carrito: resolver líneas y construir la vista."""

from __future__ import annotations

from backend.pricing import compute_totals
from backend.repositories import cart_repo, product_repo, store_repo
from backend.schemas.checkout import CartLine, CartView


def _unit_price(product, sku: str) -> float:
    if product.variants and sku != "-":
        for v in product.variants:
            if v.sku == sku:
                return round(product.price + v.price_delta, 2)
    return product.price


def resolve_lines(user_id: str) -> list[dict]:
    """Devuelve las líneas del carrito con nombre y precio unitario resueltos."""
    lines: list[dict] = []
    for item in cart_repo.list_items(user_id):
        product = product_repo.get_product(item["product_id"])
        if not product or not product.is_active:
            continue
        unit_price = _unit_price(product, item["sku"])
        lines.append(
            {
                "product_id": item["product_id"],
                "sku": item["sku"],
                "name": product.name,
                "unit_price": unit_price,
                "quantity": int(item["quantity"]),
            }
        )
    return lines


def build_cart_view(user_id: str) -> CartView:
    lines = resolve_lines(user_id)
    cart_lines = [
        CartLine(
            subtotal=round(line_data["unit_price"] * line_data["quantity"], 2),
            **line_data,
        )
        for line_data in lines
    ]
    subtotal = round(sum(cl.subtotal for cl in cart_lines), 2)
    totals = compute_totals(subtotal, store_repo.get_config())
    return CartView(lines=cart_lines, **totals)
