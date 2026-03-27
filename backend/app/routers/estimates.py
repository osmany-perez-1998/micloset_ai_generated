from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import get_current_user, require_sales_rep_or_admin
from app.models.user import User
from app.schemas.estimate import (
    PriceFetchResponse, PriceFetchResult,
    EstimateSubmit, PaymentInput,
)
from app.schemas.order import OrderRead
from app.services.estimate import fetch_prices_for_order, submit_estimate, record_payment

router = APIRouter(prefix="/orders", tags=["estimates"])


@router.get("/{order_id}/fetch-prices", response_model=PriceFetchResponse)
async def fetch_prices(
    order_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_sales_rep_or_admin),
):
    """
    Scrape prices for all items in an order.
    Returns per-item results — needs_manual=True means rep must enter price manually.
    """
    from app.models.order_item import OrderItem
    items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    if not items:
        return PriceFetchResponse(results=[], all_found=True)

    raw_results = await fetch_prices_for_order(db, order_id)

    results = [
        PriceFetchResult(
            order_item_id=item.id,
            product_url=item.product_url,
            price=r.price,
            currency=r.currency,
            store=r.store,
            method=r.method,
            needs_manual=r.needs_manual,
        )
        for item, r in zip(items, raw_results)
    ]

    return PriceFetchResponse(
        results=results,
        all_found=all(not r.needs_manual for r in results),
    )


@router.post("/{order_id}/estimate", response_model=OrderRead)
def set_estimate(
    order_id: str,
    data: EstimateSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales_rep_or_admin),
):
    """Sales rep submits confirmed prices + service fee tier → estimate sent to customer."""
    return submit_estimate(db, order_id, data, current_user)


@router.post("/{order_id}/payment", response_model=OrderRead)
def record_customer_payment(
    order_id: str,
    data: PaymentInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Record customer payment. Accepts:
      - deposit (50% of estimate)
      - full_prepay (100% of estimate, shipping billed later)
    Payment acts as acceptance of the estimate.
    """
    return record_payment(db, order_id, data, current_user)
