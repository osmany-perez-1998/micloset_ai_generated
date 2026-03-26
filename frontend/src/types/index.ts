// ─── User ────────────────────────────────────────────────────────────────────

export type UserRole = "customer" | "sales_rep" | "admin";

export interface User {
  id: string;
  full_name: string;
  email: string;
  phone?: string;
  role: UserRole;
  cuba_address?: string;
  cuba_city?: string;
  created_at: string;
}

// ─── Orders ──────────────────────────────────────────────────────────────────

export type OrderStatus =
  | "links_submitted"
  | "estimate_provided"
  | "deposit_paid"
  | "price_verified"
  | "price_changed"
  | "customer_reconfirmed"
  | "purchased"
  | "at_miami_partner"
  | "shipped_to_cuba"
  | "at_pickup_point"
  | "shipping_calculated"
  | "awaiting_final_payment"
  | "ready_for_delivery"
  | "delivered"
  | "cancelled"
  | "refunded";

export type ShippingMethod = "express_air" | "standard_air" | "maritime";
export type DeliveryPreference = "home_delivery" | "pickup";

export interface OrderItem {
  id: string;
  product_url: string;
  product_name?: string;
  store_name?: string;
  quantity: number;
  size?: string;
  color?: string;
  variant_notes?: string;
  price_at_estimate_usd?: number;
  price_at_purchase_usd?: number;
  price_changed: boolean;
  customer_confirmed_price_change?: boolean;
}

export interface Order {
  id: string;
  order_number: string;
  status: OrderStatus;
  customer: User;
  sales_rep?: User;
  items: OrderItem[];
  subtotal_usd?: number;
  service_fee_pct: number;
  service_fee_usd?: number;
  customs_estimate_usd?: number;
  shipping_charged_usd?: number;
  total_estimate_usd?: number;
  total_final_usd?: number;
  deposit_paid_usd?: number;
  deposit_payment_method?: string;
  shipping_method?: ShippingMethod;
  delivery_preference?: DeliveryPreference;
  tracking_number?: string;
  weight_kg?: number;
  customer_notes?: string;
  created_at: string;
  updated_at: string;
}

// ─── Status display helpers ───────────────────────────────────────────────────

export const ORDER_STATUS_LABELS: Record<OrderStatus, string> = {
  links_submitted: "Links Enviados",
  estimate_provided: "Estimado Enviado",
  deposit_paid: "Depósito Pagado",
  price_verified: "Precios Verificados",
  price_changed: "Precio Cambió",
  customer_reconfirmed: "Cliente Reconfirmó",
  purchased: "Comprado",
  at_miami_partner: "En Miami",
  shipped_to_cuba: "En Camino a Cuba",
  at_pickup_point: "En Punto de Recogida",
  shipping_calculated: "Flete Calculado",
  awaiting_final_payment: "Esperando Pago Final",
  ready_for_delivery: "Listo para Entrega",
  delivered: "Entregado",
  cancelled: "Cancelado",
  refunded: "Reembolsado",
};
