from datetime import datetime

from pydantic import BaseModel, field_validator

from app.models.order import OrderStatus
from app.models.payment import PaymentPhase, PaymentType
from app.models.shipment import ShippingType


class OrderItemCreate(BaseModel):
    product_url: str
    quantity: int = 1
    notes: str | None = None
    variant: str | None = None

    @field_validator("quantity")
    @classmethod
    def qty_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Quantity must be at least 1")
        return v


class OrderItemRead(BaseModel):
    id: int
    order_id: int
    product_url: str
    product_name: str | None
    product_image_url: str | None
    quantity: int
    estimated_price: float | None
    actual_price: float | None
    notes: str | None
    variant: str | None

    model_config = {"from_attributes": True}


class OrderItemUpdate(BaseModel):
    product_name: str | None = None
    product_image_url: str | None = None
    estimated_price: float | None = None
    actual_price: float | None = None
    notes: str | None = None
    variant: str | None = None


class OrderCreate(BaseModel):
    items: list[OrderItemCreate]
    notes: str | None = None


class OrderRead(BaseModel):
    id: int
    customer_id: int
    sales_rep_id: int | None
    status: OrderStatus
    service_fee_pct: float
    subtotal_estimate: float | None
    service_fee_amount: float | None
    total_estimate: float | None
    deposit_amount: float | None
    final_total: float | None
    notes: str | None
    customer_notes: str | None
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemRead] = []

    model_config = {"from_attributes": True}


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
    customer_notes: str | None = None


class EstimateCreate(BaseModel):
    service_fee_pct: float = 15.0
    items: list[OrderItemUpdate]
    customer_notes: str | None = None

    @field_validator("service_fee_pct")
    @classmethod
    def fee_in_range(cls, v: float) -> float:
        if not (0 <= v <= 20):
            raise ValueError("Service fee must be between 0% and 20%")
        return v


class PaymentCreate(BaseModel):
    amount: float
    payment_type: PaymentType
    phase: PaymentPhase
    reference: str | None = None
    notes: str | None = None


class PaymentRead(BaseModel):
    id: int
    order_id: int
    amount: float
    payment_type: PaymentType
    phase: PaymentPhase
    reference: str | None
    notes: str | None
    recorded_at: datetime

    model_config = {"from_attributes": True}


class ShipmentUpdate(BaseModel):
    shipping_type: ShippingType | None = None
    actual_weight_lbs: float | None = None
    actual_cost_usd: float | None = None
    markup_usd: float | None = None
    customs_estimate: float | None = None
    customs_actual: float | None = None
    tracking_number: str | None = None


class ShipmentRead(BaseModel):
    id: int
    order_id: int
    shipping_type: ShippingType | None
    actual_weight_lbs: float | None
    actual_cost_usd: float | None
    markup_usd: float | None
    customs_estimate: float | None
    customs_actual: float | None
    tracking_number: str | None

    model_config = {"from_attributes": True}


class PriceCheckCreate(BaseModel):
    order_item_id: int
    current_price: float


class PriceCheckRead(BaseModel):
    id: int
    order_item_id: int
    original_price: float
    current_price: float
    price_changed: bool
    client_notified: bool
    client_confirmed: bool | None

    model_config = {"from_attributes": True}
