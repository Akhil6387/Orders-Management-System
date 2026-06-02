from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.order import OrderCreate, OrderListResponse, OrderSingleResponse
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("", response_model=OrderListResponse)
def list_orders(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=200),
    db: Session = Depends(get_db),
):
    service = OrderService(db)
    orders, total = service.get_all(skip=skip, limit=limit)
    return {"success": True, "data": orders, "total": total}


@router.get("/{order_id}", response_model=OrderSingleResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    service = OrderService(db)
    order = service.get_by_id(order_id)
    return {"success": True, "data": order}


@router.post("", response_model=OrderSingleResponse, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    service = OrderService(db)
    order = service.create(payload)
    return {"success": True, "data": order}


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    service = OrderService(db)
    service.delete(order_id)
