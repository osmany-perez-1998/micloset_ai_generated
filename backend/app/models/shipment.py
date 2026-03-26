import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ShippingType(str, enum.Enum):
    EXPRESS_AIR = "EXPRESS_AIR"
    STANDARD_AIR = "STANDARD_AIR"
    MARITIME = "MARITIME"


SHIPPING_TYPE_LABELS = {
    ShippingType.EXPRESS_AIR: "Express Air",
    ShippingType.STANDARD_AIR: "Standard Air",
    ShippingType.MARITIME: "Maritime (Sea)",
}


class Shipment(Base):
    __tablename__ = "shipments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("orders.id"), nullable=False, unique=True, index=True
    )
    shipping_type: Mapped[ShippingType | None] = mapped_column(
        Enum(ShippingType), nullable=True
    )
    # Weight & cost (set in Cuba after categorizing)
    actual_weight_lbs: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_cost_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    markup_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    # Customs
    customs_estimate: Mapped[float | None] = mapped_column(Float, nullable=True)
    customs_actual: Mapped[float | None] = mapped_column(Float, nullable=True)
    # Tracking
    tracking_number: Mapped[str | None] = mapped_column(String(200), nullable=True)
    shipped_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    arrived_miami_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    arrived_cuba_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="shipment")  # noqa: F821
