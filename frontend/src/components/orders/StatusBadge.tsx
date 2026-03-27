import { OrderStatus, ORDER_STATUS_LABELS } from "@/types";
import { clsx } from "clsx";

const STATUS_COLORS: Record<OrderStatus, string> = {
  links_submitted:        "bg-gray-100 text-gray-700",
  estimate_provided:      "bg-blue-100 text-blue-700",
  deposit_paid:           "bg-purple-100 text-purple-700",
  price_verified:         "bg-purple-100 text-purple-700",
  price_changed:          "bg-yellow-100 text-yellow-700",
  customer_reconfirmed:   "bg-purple-100 text-purple-700",
  purchased:              "bg-indigo-100 text-indigo-700",
  at_miami_partner:       "bg-indigo-100 text-indigo-700",
  shipped_to_cuba:        "bg-pink-100 text-pink-700",
  at_pickup_point:        "bg-pink-100 text-pink-700",
  shipping_calculated:    "bg-orange-100 text-orange-700",
  awaiting_final_payment: "bg-orange-100 text-orange-700",
  ready_for_delivery:     "bg-green-100 text-green-700",
  delivered:              "bg-green-200 text-green-800",
  cancelled:              "bg-red-100 text-red-600",
  refunded:               "bg-red-100 text-red-600",
};

export default function StatusBadge({ status }: { status: OrderStatus }) {
  return (
    <span className={clsx("status-badge", STATUS_COLORS[status])}>
      {ORDER_STATUS_LABELS[status]}
    </span>
  );
}
