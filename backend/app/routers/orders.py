from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import get_current_user, require_sales_rep_or_admin
from app.models.user import User, UserRole
from app.schemas.order import OrderCreate, OrderRead, OrderSummary
from app.services.order import (
    create_order,
    get_customer_orders,
    get_order_detail,
    get_all_orders,
    assign_order,
)

router = APIRouter(prefix="/orders", tags=["orders"])


# ─── Customer endpoints ───────────────────────────────────────────────────────

@router.post("", response_model=OrderRead, status_code=201)
def submit_order(
    data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Customer submits product links to start an order."""
    return create_order(db, data, current_user)


@router.get("", response_model=list[OrderSummary])
def list_orders(
    status: Optional[str] = Query(None),
    mine: bool = Query(False, description="Staff only: show only orders assigned to me"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Customers: returns their own orders.
    Staff: returns all orders, with optional status and assignment filters.
    """
    is_staff = current_user.role in (UserRole.SALES_REP, UserRole.ADMIN)

    if is_staff:
        orders = get_all_orders(
            db,
            status_filter=status,
            assigned_to_me=mine,
            rep_id=current_user.id,
        )
    else:
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
    """Full order detail. Customers see only their own; staff see all."""
    return get_order_detail(db, order_id, current_user)


# ─── Staff-only endpoints ─────────────────────────────────────────────────────

@router.patch("/{order_id}/assign", response_model=OrderRead)
def assign_to_me(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales_rep_or_admin),
):
    """Sales rep assigns themselves to an order."""
    return assign_order(db, order_id, current_user)
