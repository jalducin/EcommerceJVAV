"""Endpoints de pedidos y checkout (DynamoDB)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from backend.cart_service import resolve_lines
from backend.deps import get_current_user
from backend.pricing import compute_totals
from backend.repositories import cart_repo, order_repo, store_repo
from backend.repositories.order_repo import OutOfStockError
from backend.schemas.checkout import CheckoutRequest, Order, OrderLine

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("/checkout", response_model=Order, status_code=status.HTTP_201_CREATED)
def checkout(data: CheckoutRequest, user: dict = Depends(get_current_user)) -> Order:
    lines_data = resolve_lines(user["id"])
    if not lines_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El carrito está vacío"
        )

    lines = [OrderLine(**ld) for ld in lines_data]
    subtotal = round(sum(line.unit_price * line.quantity for line in lines), 2)
    config = store_repo.get_config()
    totals = compute_totals(subtotal, config)

    # Click & collect: recoger en tienda no cobra envío y requiere ubicación válida.
    pickup_location = None
    if data.fulfillment == "pickup":
        if not config.pickup_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Recoger en tienda no está disponible",
            )
        pickup_location = next(
            (
                loc
                for loc in config.pickup_locations
                if loc.get("id") == data.pickup_location_id
            ),
            None,
        )
        if not pickup_location:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Ubicación de recogida inválida",
            )
        totals = {
            **totals,
            "shipping": 0.0,
            "total": round(totals["subtotal"] + totals["tax"], 2),
        }

    try:
        order = order_repo.create_order(
            user["id"],
            lines,
            totals,
            data.shipping_address,
            fulfillment=data.fulfillment,
            pickup_location=pickup_location,
        )
    except OutOfStockError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Stock insuficiente para uno o más productos",
        )

    cart_repo.clear(user["id"])
    return order


@router.get("", response_model=list[Order])
def my_orders(user: dict = Depends(get_current_user)) -> list[Order]:
    return order_repo.list_orders(user["id"])


@router.get("/{order_id}", response_model=Order)
def get_order(order_id: str, user: dict = Depends(get_current_user)) -> Order:
    order = order_repo.get_order(user["id"], order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado"
        )
    return order
