from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.order import OrderCreate, OrderRead, OrderSummary
from app.services.order import create_order, get_customer_orders, get_order_detail

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderRead, status_code=201)
def submit_order(
    data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Customer submits product links to start an order."""
    return create_order(db, data, current_user)


@router.get("", response_model=list[OrderSummary])
def list_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns the current customer's orders."""
    orders = get_customer_orders(db, current_user)
    return [
        OrderSummary(
            id=o.id,
            order_number=o.order_number,
            status=o.status,
            item_count=len(o.items),
            total_estimate_usd=o.total_estimate_usd,
            total_final_usd=o.total_final_usd,
            shipping_method=o.shipping_method,
            created_at=o.created_at,
        )
        for o in orders
    ]


@router.get("/{order_id}", response_model=OrderRead)
def get_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get full order detail. Customers see only their own; staff see all."""
    return get_order_detail(db, order_id, current_user)
