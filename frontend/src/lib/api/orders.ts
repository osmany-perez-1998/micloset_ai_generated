import { api } from "@/lib/api";
import { Order, OrderSummary } from "@/types";

export interface OrderItemInput {
  product_url: string;
  quantity: number;
  size?: string;
  color?: string;
  variant_notes?: string;
}

export interface CreateOrderInput {
  items: OrderItemInput[];
  shipping_method?: string;
  delivery_preference?: string;
  customer_notes?: string;
}

export async function createOrder(data: CreateOrderInput): Promise<Order> {
  const res = await api.post("/orders", data);
  return res.data;
}

export async function listMyOrders(): Promise<OrderSummary[]> {
  const res = await api.get("/orders");
  return res.data;
}

export async function getOrder(id: string): Promise<Order> {
  const res = await api.get(`/orders/${id}`);
  return res.data;
}
