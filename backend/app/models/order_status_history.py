from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class OrderStatusHistory(UUIDMixin, TimestampMixin, Base):
    """Immutable audit trail of every status transition."""
    __tablename__ = "order_status_history"

    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False)
    order = relationship("Order", back_populates="status_history")

    from_status = Column(String(50), nullable=True)
    to_status = Column(String(50), nullable=False)
    changed_by_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    note = Column(Text, nullable=True)
