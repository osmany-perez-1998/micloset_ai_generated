import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PaymentType(str, enum.Enum):
    CASH = "CASH"
    WIRE = "WIRE"


class PaymentPhase(str, enum.Enum):
    DEPOSIT = "DEPOSIT"
    FINAL = "FINAL"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("orders.id"), nullable=False, index=True
    )
    recorded_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    payment_type: Mapped[PaymentType] = mapped_column(
        Enum(PaymentType), nullable=False
    )
    phase: Mapped[PaymentPhase] = mapped_column(Enum(PaymentPhase), nullable=False)
    reference: Mapped[str | None] = mapped_column(String(200), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="payments")  # noqa: F821
