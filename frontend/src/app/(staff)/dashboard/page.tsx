"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { format } from "date-fns";
import { es } from "date-fns/locale";
import RouteGuard from "@/components/layout/RouteGuard";
import StatusBadge from "@/components/orders/StatusBadge";
import { listAllOrders, assignOrder } from "@/lib/api/staff";
import { OrderSummary, OrderStatus, ORDER_STATUS_LABELS } from "@/types";
import { useAuthStore } from "@/lib/store/auth";

const STATUSES: { value: string; label: string }[] = [
  { value: "", label: "Todos" },
  ...Object.entries(ORDER_STATUS_LABELS).map(([value, label]) => ({ value, label })),
];

const SHIPPING_LABELS: Record<string, string> = {
  express_air: "Aéreo Express",
  standard_air: "Aéreo Estándar",
  maritime: "Marítimo",
};

export default function SalesRepDashboard() {
  const { user, logout } = useAuthStore();
  const [orders, setOrders] = useState<OrderSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("");
  const [mineOnly, setMineOnly] = useState(false);
  const [assigning, setAssigning] = useState<string | null>(null);

  const fetchOrders = useCallback(async () => {
    setLoading(true);
    try {
      const data = await listAllOrders({
        status: statusFilter || undefined,
        mine: mineOnly || undefined,
      });
      setOrders(data);
    } finally {
      setLoading(false);
    }
  }, [statusFilter, mineOnly]);

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  async function handleAssign(orderId: string) {
    setAssigning(orderId);
    try {
      await assignOrder(orderId);
      await fetchOrders();
    } finally {
      setAssigning(null);
    }
  }

  return (
    <RouteGuard allowedRoles={["sales_rep", "admin"]}>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-brand-violet px-4 py-3 flex items-center justify-between">
          <h1 className="font-brielle text-xl text-white">Mi Closet — Dashboard</h1>
          <div className="flex items-center gap-3">
            <span className="text-brand-pink-lightest text-sm hidden sm:block">
              {user?.full_name}
            </span>
            <button onClick={logout} className="text-brand-pink-lightest text-xs hover:underline">
              Salir
            </button>
          </div>
        </header>

        <main className="max-w-4xl mx-auto px-4 py-6 space-y-4">
          {/* Filters */}
          <div className="card">
            <div className="flex flex-wrap gap-3 items-end">
              <div className="flex-1 min-w-[180px]">
                <label className="block text-xs font-medium text-gray-500 mb-1">Estado</label>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="w-full border border-gray-200 rounded-brand px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-brand-violet"
                >
                  {STATUSES.map((s) => (
                    <option key={s.value} value={s.value}>
                      {s.label}
                    </option>
                  ))}
                </select>
              </div>

              <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer pb-2">
                <input
                  type="checkbox"
                  checked={mineOnly}
                  onChange={(e) => setMineOnly(e.target.checked)}
                  className="accent-brand-violet"
                />
                Solo mis pedidos
              </label>

              <button
                onClick={fetchOrders}
                className="btn-secondary text-sm pb-2"
              >
                Actualizar
              </button>
            </div>
          </div>

          {/* Stats bar */}
          <div className="flex items-center justify-between text-sm text-gray-500 px-1">
            <span>
              {loading ? "Cargando..." : `${orders.length} pedido${orders.length !== 1 ? "s" : ""}`}
            </span>
          </div>

          {/* Order cards */}
          {!loading && orders.length === 0 && (
            <div className="card text-center py-10 text-gray-400">
              No hay pedidos que coincidan con los filtros.
            </div>
          )}

          <div className="space-y-3">
            {orders.map((order) => (
              <div key={order.id} className="card">
                <div className="flex items-start justify-between gap-4 flex-wrap">
                  {/* Left: order info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 flex-wrap">
                      <Link
                        href={`/dashboard/orders/${order.id}`}
                        className="font-semibold text-gray-900 hover:text-brand-violet"
                      >
                        {order.order_number}
                      </Link>
                      <StatusBadge status={order.status as OrderStatus} />
                    </div>

                    <div className="flex flex-wrap gap-x-4 gap-y-1 mt-1 text-xs text-gray-400">
                      <span>
                        {format(new Date(order.created_at), "d MMM yyyy · HH:mm", { locale: es })}
                      </span>
                      <span>
                        {order.item_count} {order.item_count === 1 ? "producto" : "productos"}
                      </span>
                      {order.shipping_method && (
                        <span>{SHIPPING_LABELS[order.shipping_method]}</span>
                      )}
                    </div>

                    {order.total_estimate_usd != null && (
                      <p className="text-sm text-gray-600 mt-2">
                        Estimado:{" "}
                        <span className="font-semibold text-brand-violet">
                          ${order.total_estimate_usd.toFixed(2)} USD
                        </span>
                      </p>
                    )}
                  </div>

                  {/* Right: actions */}
                  <div className="flex gap-2 items-start">
                    <Link
                      href={`/dashboard/orders/${order.id}`}
                      className="btn-secondary text-xs py-1.5 px-3"
                    >
                      Ver
                    </Link>
                    {order.status === "links_submitted" && (
                      <button
                        onClick={() => handleAssign(order.id)}
                        disabled={assigning === order.id}
                        className="btn-primary text-xs py-1.5 px-3 disabled:opacity-60"
                      >
                        {assigning === order.id ? "..." : "Asignar"}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </main>
      </div>
    </RouteGuard>
  );
}
