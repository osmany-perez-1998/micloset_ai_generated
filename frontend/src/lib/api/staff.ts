import { api } from "@/lib/api";
import { Order, OrderSummary } from "@/types";

export async function listAllOrders(params?: {
  status?: string;
  mine?: boolean;
}): Promise<OrderSummary[]> {
  const res = await api.get("/orders", { params });
  return res.data;
}

export async function assignOrder(orderId: string): Promise<Order> {
  const res = await api.patch(`/orders/${orderId}/assign`);
  return res.data;
}

// ─── Estimate engine ──────────────────────────────────────────────────────────

export interface PriceFetchResult {
  order_item_id: string;
  product_url: string;
  price: number | null;
  currency: string | null;
  store: string | null;
  method: string | null;
  needs_manual: boolean;
}

export interface PriceFetchResponse {
  results: PriceFetchResult[];
  all_found: boolean;
}

export async function fetchPrices(orderId: string): Promise<PriceFetchResponse> {
  const res = await api.get(`/orders/${orderId}/fetch-prices`);
  return res.data;
}

export interface ItemPriceInput {
  order_item_id: string;
  price_usd: number;
}

export interface EstimateSubmitInput {
  item_prices: ItemPriceInput[];
  service_fee_pct: number;
}

export async function submitEstimate(orderId: string, data: EstimateSubmitInput): Promise<Order> {
  const res = await api.post(`/orders/${orderId}/estimate`, data);
  return res.data;
}
