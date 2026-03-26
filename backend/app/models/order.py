from sqlalchemy import Column, String, Float, Enum, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin
import enum


class OrderStatus(str, enum.Enum):
    # Step 1-2: Customer submits links
    LINKS_SUBMITTED = "links_submitted"
    # Step 3: Sales rep provides estimate
    ESTIMATE_PROVIDED = "estimate_provided"
    # Step 4: Customer pays deposit
    DEPOSIT_PAID = "deposit_paid"
    # Step 5-6: Price verification
    PRICE_VERIFIED = "price_verified"
    PRICE_CHANGED = "price_changed"          # customer must confirm
    CUSTOMER_RECONFIRMED = "customer_reconfirmed"
    # Step 7: Products purchased
    PURCHASED = "purchased"
    # Step 8: Delivered to Miami partner
    AT_MIAMI_PARTNER = "at_miami_partner"
    # Step 9: Shipped to Cuba
    SHIPPED_TO_CUBA = "shipped_to_cuba"
    # Step 10: Received at pickup point
    AT_PICKUP_POINT = "at_pickup_point"
    # Step 11-12: Sorted, weighed, shipping calculated
    SHIPPING_CALCULATED = "shipping_calculated"
    # Step 13: Awaiting final payment & delivery
    AWAITING_FINAL_PAYMENT = "awaiting_final_payment"
    READY_FOR_DELIVERY = "ready_for_delivery"
    DELIVERED = "delivered"
    # Edge cases
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class ShippingMethod(str, enum.Enum):
    EXPRESS_AIR = "express_air"
    STANDARD_AIR = "standard_air"
    MARITIME = "maritime"


class DeliveryPreference(str, enum.Enum):
    HOME_DELIVERY = "home_delivery"
    PICKUP = "pickup"


class Order(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "orders"

    order_number = Column(String(20), unique=True, nullable=False, index=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.LINKS_SUBMITTED, nullable=False)

    # Relationships
    customer_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    sales_rep_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    customer = relationship("User", back_populates="orders", foreign_keys=[customer_id])
    sales_rep = relationship("User", back_populates="assigned_orders", foreign_keys=[sales_rep_id])

    # Financials (USD)
    subtotal_usd = Column(Float, nullable=True)           # sum of product prices
    service_fee_pct = Column(Float, default=0.15)         # e.g. 0.15 = 15%
    service_fee_usd = Column(Float, nullable=True)
    customs_estimate_usd = Column(Float, nullable=True)
    shipping_cost_actual_usd = Column(Float, nullable=True)   # what Miami partner charges us
    shipping_markup_usd = Column(Float, default=1.25)         # our markup (covers packing)
    shipping_charged_usd = Column(Float, nullable=True)       # what we charge customer
    total_estimate_usd = Column(Float, nullable=True)         # before shipping known
    total_final_usd = Column(Float, nullable=True)            # final amount

    # Payments
    deposit_paid_usd = Column(Float, nullable=True)
    deposit_payment_method = Column(String(50), nullable=True)  # cash, wire
    final_payment_usd = Column(Float, nullable=True)
    final_payment_method = Column(String(50), nullable=True)

    # Shipping
    shipping_method = Column(Enum(ShippingMethod), nullable=True)
    delivery_preference = Column(Enum(DeliveryPreference), nullable=True)
    tracking_number = Column(String(100), nullable=True)
    weight_kg = Column(Float, nullable=True)

    # Notes
    internal_notes = Column(Text, nullable=True)    # only visible to staff
    customer_notes = Column(Text, nullable=True)

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    status_history = relationship("OrderStatusHistory", back_populates="order", cascade="all, delete-orphan")
