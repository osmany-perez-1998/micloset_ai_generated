from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime
from app.models.order import OrderStatus, ShippingMethod, DeliveryPreference
from app.schemas.user import UserRead


# ─── Order Item ──────────────────────────────────────────────────────────────

class OrderItemCreate(BaseModel):
    product_url: str
    quantity: int = 1
    size: Optional[str] = None
    color: Optional[str] = None
    variant_notes: Optional[str] = None


class OrderItemRead(BaseModel):
    id: str
    product_url: str
    product_name: Optional[str] = None
    store_name: Optional[str] = None
    quantity: int
    size: Optional[str] = None
    color: Optional[str] = None
    variant_notes: Optional[str] = None
    price_at_estimate_usd: Optional[float] = None
    price_at_purchase_usd: Optional[float] = None
    price_changed: bool

    class Config:
        from_attributes = True


# ─── Order ───────────────────────────────────────────────────────────────────

class OrderCreate(BaseModel):
    items: list[OrderItemCreate]
    shipping_method: Optional[ShippingMethod] = None
    delivery_preference: Optional[DeliveryPreference] = None
    customer_notes: Optional[str] = None


class OrderRead(BaseModel):
    id: str
    order_number: str
    status: OrderStatus
    customer: UserRead
    sales_rep: Optional[UserRead] = None
    items: list[OrderItemRead]

    # Financials
    subtotal_usd: Optional[float] = None
    service_fee_pct: float
    service_fee_usd: Optional[float] = None
    customs_estimate_usd: Optional[float] = None
    shipping_charged_usd: Optional[float] = None
    total_estimate_usd: Optional[float] = None
    total_final_usd: Optional[float] = None
    deposit_paid_usd: Optional[float] = None
    deposit_payment_method: Optional[str] = None

    # Shipping
    shipping_method: Optional[ShippingMethod] = None
    delivery_preference: Optional[DeliveryPreference] = None
    tracking_number: Optional[str] = None
    weight_kg: Optional[float] = None

    customer_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderSummary(BaseModel):
    """Lightweight version for list views."""
    id: str
    order_number: str
    status: OrderStatus
    item_count: int
    total_estimate_usd: Optional[float] = None
    total_final_usd: Optional[float] = None
    shipping_method: Optional[ShippingMethod] = None
    created_at: datetime

    class Config:
        from_attributes = True
