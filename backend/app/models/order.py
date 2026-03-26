import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class OrderStatus(str, enum.Enum):
    SUBMITTED = "SUBMITTED"
    ESTIMATED = "ESTIMATED"
    AWAITING_DEPOSIT = "AWAITING_DEPOSIT"
    DEPOSIT_RECEIVED = "DEPOSIT_RECEIVED"
    PRICE_VERIFICATION = "PRICE_VERIFICATION"
    PURCHASING = "PURCHASING"
    SHIPPED_TO_MIAMI = "SHIPPED_TO_MIAMI"
    RECEIVED_IN_MIAMI = "RECEIVED_IN_MIAMI"
    IN_TRANSIT_TO_CUBA = "IN_TRANSIT_TO_CUBA"
    RECEIVED_IN_CUBA = "RECEIVED_IN_CUBA"
    CATEGORIZING = "CATEGORIZING"
    FINAL_INVOICE_SENT = "FINAL_INVOICE_SENT"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


# Human-readable labels for each status (used in frontend timeline)
ORDER_STATUS_LABELS = {
    OrderStatus.SUBMITTED: "Order Submitted",
    OrderStatus.ESTIMATED: "Estimate Ready",
    OrderStatus.AWAITING_DEPOSIT: "Awaiting Deposit",
    OrderStatus.DEPOSIT_RECEIVED: "Deposit Received",
    OrderStatus.PRICE_VERIFICATION: "Verifying Prices",
    OrderStatus.PURCHASING: "Purchasing Items",
    OrderStatus.SHIPPED_TO_MIAMI: "Shipped to Miami",
    OrderStatus.RECEIVED_IN_MIAMI: "Received in Miami",
    OrderStatus.IN_TRANSIT_TO_CUBA: "In Transit to Cuba",
    OrderStatus.RECEIVED_IN_CUBA: "Arrived in Cuba",
    OrderStatus.CATEGORIZING: "Sorting Your Items",
    OrderStatus.FINAL_INVOICE_SENT: "Final Invoice Sent",
    OrderStatus.COMPLETED: "Delivered",
    OrderStatus.CANCELLED: "Cancelled",
}


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    sales_rep_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), default=OrderStatus.SUBMITTED, nullable=False, index=True
    )
    service_fee_pct: Mapped[float] = mapped_column(Float, default=15.0, nullable=False)
    # Calculated totals (denormalized for quick display)
    subtotal_estimate: Mapped[float | None] = mapped_column(Float, nullable=True)
    service_fee_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_estimate: Mapped[float | None] = mapped_column(Float, nullable=True)
    deposit_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    final_total: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Customer-facing notes (visible to customer)
    customer_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    customer: Mapped["User"] = relationship(  # noqa: F821
        "User", foreign_keys=[customer_id], back_populates="customer_orders"
    )
    sales_rep: Mapped["User | None"] = relationship(  # noqa: F821
        "User", foreign_keys=[sales_rep_id], back_populates="rep_orders"
    )
    items: Mapped[list["OrderItem"]] = relationship(  # noqa: F821
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )
    payments: Mapped[list["Payment"]] = relationship(  # noqa: F821
        "Payment", back_populates="order", cascade="all, delete-orphan"
    )
    shipment: Mapped["Shipment | None"] = relationship(  # noqa: F821
        "Shipment", back_populates="order", uselist=False
    )
