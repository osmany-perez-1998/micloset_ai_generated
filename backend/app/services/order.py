from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.order_status_history import OrderStatusHistory
from app.models.user import User, UserRole
from app.schemas.order import OrderCreate
from app.utils.order_number import generate_order_number


def create_order(db: Session, data: OrderCreate, customer: User) -> Order:
    if not data.items:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="An order must have at least one item.",
        )

    order = Order(
        order_number=generate_order_number(db),
        status=OrderStatus.LINKS_SUBMITTED,
        customer_id=customer.id,
        shipping_method=data.shipping_method,
        delivery_preference=data.delivery_preference,
        customer_notes=data.customer_notes,
    )
    db.add(order)
    db.flush()  # get order.id before adding items

    for item_data in data.items:
        db.add(OrderItem(
            order_id=order.id,
            product_url=str(item_data.product_url),
            quantity=item_data.quantity,
            size=item_data.size,
            color=item_data.color,
            variant_notes=item_data.variant_notes,
        ))

    db.add(OrderStatusHistory(
        order_id=order.id,
        from_status=None,
        to_status=OrderStatus.LINKS_SUBMITTED.value,
        changed_by_id=customer.id,
        note="Order created by customer.",
    ))

    db.commit()
    db.refresh(order)
    return order


def get_customer_orders(db: Session, customer: User) -> list[Order]:
    return (
        db.query(Order)
        .filter(Order.customer_id == customer.id)
        .order_by(Order.created_at.desc())
        .all()
    )


def get_order_detail(db: Session, order_id: str, requester: User) -> Order:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")

    # Customers can only see their own orders
    is_staff = requester.role in (UserRole.SALES_REP, UserRole.ADMIN)
    if not is_staff and order.customer_id != requester.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    return order
