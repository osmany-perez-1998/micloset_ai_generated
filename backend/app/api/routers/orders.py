from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_sales_rep
from app.core.database import get_db
from app.models.order import OrderStatus
from app.models.user import User, UserRole
from app.schemas.order import (
    EstimateCreate,
    OrderCreate,
    OrderItemUpdate,
    OrderRead,
    OrderStatusUpdate,
    PaymentCreate,
    PaymentRead,
    PriceCheckCreate,
    PriceCheckRead,
    ShipmentRead,
    ShipmentUpdate,
)
from app.services import order as order_service

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(
    data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return order_service.create_order(db, current_user, data)


@router.get("/my", response_model=list[OrderRead])
def list_my_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return order_service.get_orders_for_customer(db, current_user.id)


@router.get("/", response_model=list[OrderRead])
def list_all_orders(
    status_filter: OrderStatus | None = Query(None, alias="status"),
    current_user: User = Depends(require_sales_rep),
    db: Session = Depends(get_db),
):
    return order_service.get_all_orders(db, status_filter)


@router.get("/{order_id}", response_model=OrderRead)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = order_service.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if current_user.role == UserRole.CUSTOMER and order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return order


@router.patch("/{order_id}/items/{item_id}", response_model=OrderRead)
def update_order_item(
    order_id: int,
    item_id: int,
    data: OrderItemUpdate,
    current_user: User = Depends(require_sales_rep),
    db: Session = Depends(get_db),
):
    order = order_service.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    item = order_service.update_item_price(db, item_id, data)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.refresh(order)
    return order


@router.post("/{order_id}/estimate", response_model=OrderRead)
def create_estimate(
    order_id: int,
    data: EstimateCreate,
    current_user: User = Depends(require_sales_rep),
    db: Session = Depends(get_db),
):
    order = order_service.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order_service.create_estimate(db, order, current_user, data)


@router.patch("/{order_id}/status", response_model=OrderRead)
def update_status(
    order_id: int,
    data: OrderStatusUpdate,
    current_user: User = Depends(require_sales_rep),
    db: Session = Depends(get_db),
):
    order = order_service.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order_service.update_order_status(db, order, data.status, data.customer_notes)


@router.post("/{order_id}/payments", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
def record_payment(
    order_id: int,
    data: PaymentCreate,
    current_user: User = Depends(require_sales_rep),
    db: Session = Depends(get_db),
):
    order = order_service.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order_service.record_payment(db, order, current_user, data)


@router.put("/{order_id}/shipment", response_model=ShipmentRead)
def upsert_shipment(
    order_id: int,
    data: ShipmentUpdate,
    current_user: User = Depends(require_sales_rep),
    db: Session = Depends(get_db),
):
    order = order_service.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order_service.upsert_shipment(db, order, data)


@router.post("/{order_id}/price-checks", response_model=PriceCheckRead, status_code=status.HTTP_201_CREATED)
def create_price_check(
    order_id: int,
    data: PriceCheckCreate,
    current_user: User = Depends(require_sales_rep),
    db: Session = Depends(get_db),
):
    order = order_service.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    try:
        return order_service.create_price_check(db, current_user, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
