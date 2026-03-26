from sqlalchemy import Column, String, Boolean, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin
import enum


class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    SALES_REP = "sales_rep"
    ADMIN = "admin"


class User(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "users"

    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(50), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER, nullable=False)
    is_active = Column(Boolean, default=True)

    # Cuba-specific: delivery address in Cuba
    cuba_address = Column(String(500), nullable=True)
    cuba_city = Column(String(100), nullable=True)

    orders = relationship("Order", back_populates="customer", foreign_keys="Order.customer_id")
    assigned_orders = relationship("Order", back_populates="sales_rep", foreign_keys="Order.sales_rep_id")
