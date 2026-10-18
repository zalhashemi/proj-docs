from fastapi import APIRouter, Depends, HTTPException

from app.auth import require_api_key
from app.schemas import OrderIn, OrderOut

router = APIRouter(prefix="/orders", tags=["orders"], dependencies=[Depends(require_api_key)])


@router.get("")
def list_orders(limit: int = 50) -> list[OrderOut]:
    return []


@router.post("", status_code=201)
def create_order(order: OrderIn) -> OrderOut:
    raise HTTPException(status_code=501, detail="not implemented")


@router.get("/{order_id}")
def get_order(order_id: int) -> OrderOut:
    raise HTTPException(status_code=404, detail="order not found")


@router.delete("/{order_id}", status_code=204)
def cancel_order(order_id: int) -> None:
    return None
