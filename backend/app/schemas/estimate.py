from pydantic import BaseModel
from typing import Optional

SERVICE_FEE_TIERS = [0, 7, 10, 15, 17, 20]


class PriceFetchResult(BaseModel):
    order_item_id: str
    product_url: str
    price: Optional[float] = None
    currency: Optional[str] = None
    store: Optional[str] = None
    method: Optional[str] = None   # json-ld | meta | css | openai
    needs_manual: bool


class PriceFetchResponse(BaseModel):
    results: list[PriceFetchResult]
    all_found: bool


class ItemPriceInput(BaseModel):
    order_item_id: str
    price_usd: float             # rep-confirmed price (auto or manually entered)


class EstimateSubmit(BaseModel):
    item_prices: list[ItemPriceInput]
    service_fee_pct: int         # must be one of SERVICE_FEE_TIERS (0,7,10,15,17,20)


class EstimateBreakdown(BaseModel):
    subtotal_usd: float
    service_fee_pct: float
    service_fee_usd: float
    total_estimate_usd: float
    deposit_required_usd: float  # 50% of total_estimate


class PaymentInput(BaseModel):
    payment_type: str            # "deposit" | "full_prepay"
    amount_usd: float
    payment_method: str          # "cash" | "wire_transfer"
