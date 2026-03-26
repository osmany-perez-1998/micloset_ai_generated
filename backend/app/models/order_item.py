from sqlalchemy import Column, String, Float, Integer, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class OrderItem(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "order_items"

    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False)
    order = relationship("Order", back_populates="items")

    product_url = Column(Text, nullable=False)
    product_name = Column(String(500), nullable=True)      # filled after rep reviews
    store_name = Column(String(100), nullable=True)        # Amazon, Shein, etc.
    quantity = Column(Integer, default=1)
    size = Column(String(50), nullable=True)
    color = Column(String(50), nullable=True)
    variant_notes = Column(Text, nullable=True)            # e.g. "size M, blue"

    # Pricing
    price_at_estimate_usd = Column(Float, nullable=True)   # price when estimate was given
    price_at_purchase_usd = Column(Float, nullable=True)   # actual purchase price
    price_changed = Column(Boolean, default=False)          # flag if price differed

    customer_confirmed_price_change = Column(Boolean, nullable=True)  # null = pending
