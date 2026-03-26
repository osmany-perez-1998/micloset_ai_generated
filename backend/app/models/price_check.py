from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PriceCheck(Base):
    __tablename__ = "price_checks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("order_items.id"), nullable=False, index=True
    )
    checked_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    original_price: Mapped[float] = mapped_column(Float, nullable=False)
    current_price: Mapped[float] = mapped_column(Float, nullable=False)
    price_changed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    client_notified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    client_confirmed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    order_item: Mapped["OrderItem"] = relationship(  # noqa: F821
        "OrderItem", back_populates="price_checks"
    )
