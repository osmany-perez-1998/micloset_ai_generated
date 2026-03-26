from sqlalchemy.orm import Session

from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.payment import Payment
from app.models.shipment import Shipment
from app.models.price_check import PriceCheck
from app.models.user import User, UserRole
from app.schemas.order import (
    OrderCreate,
    EstimateCreate,
    PaymentCreate,
    ShipmentUpdate,
    PriceCheckCreate,
    OrderItemUpdate,
)


def create_order(db: Session, customer: User, data: OrderCreate) -> Order:
    order = Order(
        customer_id=customer.id,
        status=OrderStatus.SUBMITTED,
        notes=data.notes,
    )
    db.add(order)
    db.flush()

    for item_data in data.items:
        item = OrderItem(
            order_id=order.id,
            product_url=str(item_data.product_url),
            quantity=item_data.quantity,
            notes=item_data.notes,
            variant=item_data.variant,
        )
        db.add(item)

    db.commit()
    db.refresh(order)
    return order


def get_order(db: Session, order_id: int) -> Order | None:
    return db.query(Order).filter(Order.id == order_id).first()


def get_orders_for_customer(db: Session, customer_id: int) -> list[Order]:
    return (
        db.query(Order)
        .filter(Order.customer_id == customer_id)
        .order_by(Order.created_at.desc())
        .all()
    )


def get_all_orders(db: Session, status: OrderStatus | None = None) -> list[Order]:
    q = db.query(Order)
    if status:
        q = q.filter(Order.status == status)
    return q.order_by(Order.created_at.desc()).all()


def create_estimate(db: Session, order: Order, rep: User, data: EstimateCreate) -> Order:
    order.sales_rep_id = rep.id
    order.service_fee_pct = data.service_fee_pct
    order.customer_notes = data.customer_notes

    item_map = {item.id: item for item in order.items}
    for item_update in data.items:
        pass

    subtotal = sum(
        (item.estimated_price or 0) * item.quantity for item in order.items
    )
    fee = round(subtotal * data.service_fee_pct / 100, 2)
    total = round(subtotal + fee, 2)

    order.subtotal_estimate = round(subtotal, 2)
    order.service_fee_amount = fee
    order.total_estimate = total
    order.deposit_amount = round(total / 2, 2)
    order.status = OrderStatus.ESTIMATED

    db.commit()
    db.refresh(order)
    return order


def update_item_price(db: Session, item_id: int, data: OrderItemUpdate) -> OrderItem | None:
    item = db.query(OrderItem).filter(OrderItem.id == item_id).first()
    if not item:
        return None
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    _recalculate_order(db, item.order_id)
    return item


def _recalculate_order(db: Session, order_id: int) -> None:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return
    subtotal = sum(
        (item.estimated_price or 0) * item.quantity for item in order.items
    )
    fee = round(subtotal * order.service_fee_pct / 100, 2)
    total = round(subtotal + fee, 2)
    order.subtotal_estimate = round(subtotal, 2)
    order.service_fee_amount = fee
    order.total_estimate = total
    order.deposit_amount = round(total / 2, 2)
    db.commit()


def update_order_status(db: Session, order: Order, status: OrderStatus, customer_notes: str | None = None) -> Order:
    order.status = status
    if customer_notes is not None:
        order.customer_notes = customer_notes
    db.commit()
    db.refresh(order)
    return order


def record_payment(db: Session, order: Order, recorder: User, data: PaymentCreate) -> Payment:
    payment = Payment(
        order_id=order.id,
        recorded_by=recorder.id,
        amount=data.amount,
        payment_type=data.payment_type,
        phase=data.phase,
        reference=data.reference,
        notes=data.notes,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


def upsert_shipment(db: Session, order: Order, data: ShipmentUpdate) -> Shipment:
    shipment = order.shipment
    if not shipment:
        shipment = Shipment(order_id=order.id)
        db.add(shipment)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(shipment, field, value)
    db.commit()
    db.refresh(shipment)
    return shipment


def create_price_check(db: Session, checker: User, data: PriceCheckCreate) -> PriceCheck:
    item = db.query(OrderItem).filter(OrderItem.id == data.order_item_id).first()
    if not item:
        raise ValueError("Order item not found")
    original = item.estimated_price or item.actual_price or 0
    changed = abs(data.current_price - original) > 0.01
    check = PriceCheck(
        order_item_id=data.order_item_id,
        checked_by=checker.id,
        original_price=original,
        current_price=data.current_price,
        price_changed=changed,
    )
    db.add(check)
    db.commit()
    db.refresh(check)
    return check
