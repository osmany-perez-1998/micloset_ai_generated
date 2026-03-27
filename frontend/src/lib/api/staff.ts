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
