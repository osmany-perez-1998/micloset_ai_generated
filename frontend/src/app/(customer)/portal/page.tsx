"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { format } from "date-fns";
import { es } from "date-fns/locale";
import RouteGuard from "@/components/layout/RouteGuard";
import StatusBadge from "@/components/orders/StatusBadge";
import { listMyOrders } from "@/lib/api/orders";
import { OrderSummary } from "@/types";
import { useAuthStore } from "@/lib/store/auth";

export default function CustomerPortal() {
  const { user } = useAuthStore();
  const [orders, setOrders] = useState<OrderSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listMyOrders()
      .then(setOrders)
      .finally(() => setLoading(false));
  }, []);

  return (
    <RouteGuard allowedRoles={["customer"]}>
      <div className="min-h-screen bg-brand-pink-lightest">
        {/* Header */}
        <header className="bg-brand-violet px-6 py-4 flex items-center justify-between">
          <h1 className="font-brielle text-2xl text-white">Mi Closet</h1>
          <span className="text-brand-pink-lightest text-sm">{user?.full_name}</span>
        </header>

        <main className="max-w-2xl mx-auto px-4 py-8 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="font-brielle text-2xl text-brand-violet">Mis Pedidos</h2>
            <Link href="/portal/orders/new" className="btn-primary text-sm">
              + Nuevo pedido
            </Link>
          </div>

          {loading && (
            <p className="text-gray-400 text-sm text-center py-10">Cargando pedidos...</p>
          )}

          {!loading && orders.length === 0 && (
            <div className="card text-center py-12">
              <p className="text-gray-500 mb-4">Aún no tienes pedidos.</p>
              <Link href="/portal/orders/new" className="btn-primary">
                Hacer mi primer pedido
              </Link>
            </div>
          )}

          {!loading && orders.length > 0 && (
            <div className="space-y-3">
              {orders.map((order) => (
                <Link key={order.id} href={`/portal/orders/${order.id}`}>
                  <div className="card hover:shadow-md transition-shadow cursor-pointer">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <p className="font-semibold text-gray-900">{order.order_number}</p>
                        <p className="text-xs text-gray-400 mt-0.5">
                          {format(new Date(order.created_at), "d MMM yyyy", { locale: es })}
                          {" · "}
                          {order.item_count} {order.item_count === 1 ? "producto" : "productos"}
                        </p>
                      </div>
                      <StatusBadge status={order.status} />
                    </div>

                    {order.total_estimate_usd != null && (
                      <p className="text-sm text-gray-600 mt-3">
                        Estimado:{" "}
                        <span className="font-semibold text-brand-violet">
                          ${order.total_estimate_usd.toFixed(2)} USD
                        </span>
                      </p>
                    )}
                    {order.total_final_usd != null && (
                      <p className="text-sm text-gray-600">
                        Total final:{" "}
                        <span className="font-semibold text-brand-violet">
                          ${order.total_final_usd.toFixed(2)} USD
                        </span>
                      </p>
                    )}
                  </div>
                </Link>
              ))}
            </div>
          )}
        </main>
      </div>
    </RouteGuard>
  );
}
