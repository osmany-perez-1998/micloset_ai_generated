from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.order_status_history import OrderStatusHistory
from app.models.user import User
from app.schemas.estimate import EstimateSubmit, PaymentInput, SERVICE_FEE_TIERS
from app.services.price_scraper import fetch_price, PriceResult


async def fetch_prices_for_order(db: Session, order_id: str) -> list[PriceResult]:
    """Scrape prices for every item in the order concurrently."""
    import asyncio

    items: list[OrderItem] = (
        db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    )
    if not items:
        return []

    tasks = [fetch_price(item.product_url) for item in items]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    price_results = []
    for item, result in zip(items, results):
        if isinstance(result, Exception):
            from app.services.price_scraper import PriceResult as PR
            result = PR(
                url=item.product_url, price=None, currency=None,
                store=None, method=None, raw_text=None, needs_manual=True,
            )
        price_results.append(result)

    return price_results


def submit_estimate(db: Session, order_id: str, data: EstimateSubmit, rep: User) -> Order:
    if data.service_fee_pct not in SERVICE_FEE_TIERS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Service fee must be one of {SERVICE_FEE_TIERS}.",
        )

    order: Order | None = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")

    if order.status not in (OrderStatus.LINKS_SUBMITTED, OrderStatus.PRICE_CHANGED):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot set estimate on order with status '{order.status.value}'.",
        )

    # Map item_id → price
    price_map = {p.order_item_id: p.price_usd for p in data.item_prices}

    items: list[OrderItem] = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    subtotal = 0.0
    for item in items:
        price = price_map.get(item.id)
        if price is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Missing price for item {item.id}.",
            )
        item.price_at_estimate_usd = round(price * item.quantity, 2)
        subtotal += item.price_at_estimate_usd

    fee_pct = data.service_fee_pct / 100
    fee_usd = round(subtotal * fee_pct, 2)
    total = round(subtotal + fee_usd, 2)

    order.subtotal_usd = round(subtotal, 2)
    order.service_fee_pct = fee_pct
    order.service_fee_usd = fee_usd
    order.total_estimate_usd = total
    order.status = OrderStatus.ESTIMATE_PROVIDED
    order.sales_rep_id = rep.id

    db.add(OrderStatusHistory(
        order_id=order.id,
        from_status=OrderStatus.LINKS_SUBMITTED.value,
        to_status=OrderStatus.ESTIMATE_PROVIDED.value,
        changed_by_id=rep.id,
        note=f"Estimate set: ${total} USD (fee {data.service_fee_pct}%).",
    ))

    db.commit()
    db.refresh(order)
    return order


def record_payment(db: Session, order_id: str, data: PaymentInput, actor: User) -> Order:
    order: Order | None = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")

    if order.status != OrderStatus.ESTIMATE_PROVIDED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Payment can only be recorded after an estimate is provided.",
        )

    if data.payment_type not in ("deposit", "full_prepay"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="payment_type must be 'deposit' or 'full_prepay'.",
        )

    if data.payment_method not in ("cash", "wire_transfer"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="payment_method must be 'cash' or 'wire_transfer'.",
        )

    order.deposit_paid_usd = round(data.amount_usd, 2)
    order.deposit_payment_method = data.payment_method
    order.status = OrderStatus.DEPOSIT_PAID

    db.add(OrderStatusHistory(
        order_id=order.id,
        from_status=OrderStatus.ESTIMATE_PROVIDED.value,
        to_status=OrderStatus.DEPOSIT_PAID.value,
        changed_by_id=actor.id,
        note=(
            f"{'Full prepayment' if data.payment_type == 'full_prepay' else 'Deposit'} "
            f"of ${data.amount_usd:.2f} received via {data.payment_method}."
        ),
    ))

    db.commit()
    db.refresh(order)
    return order
