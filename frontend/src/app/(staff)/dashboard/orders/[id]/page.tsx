"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { format } from "date-fns";
import { es } from "date-fns/locale";
import RouteGuard from "@/components/layout/RouteGuard";
import StatusBadge from "@/components/orders/StatusBadge";
import { getOrder } from "@/lib/api/orders";
import { assignOrder } from "@/lib/api/staff";
import { Order, ORDER_STATUS_LABELS } from "@/types";
import { useAuthStore } from "@/lib/store/auth";

const SHIPPING_LABELS: Record<string, string> = {
  express_air: "Aéreo Express",
  standard_air: "Aéreo Estándar",
  maritime: "Marítimo",
};

const DELIVERY_LABELS: Record<string, string> = {
  home_delivery: "Entrega a domicilio",
  pickup: "Recoger en punto",
};

export default function StaffOrderDetail({ params }: { params: { id: string } }) {
  const { user } = useAuthStore();
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);
  const [assigning, setAssigning] = useState(false);

  useEffect(() => {
    getOrder(params.id)
      .then(setOrder)
      .finally(() => setLoading(false));
  }, [params.id]);

  async function handleAssign() {
    setAssigning(true);
    try {
      const updated = await assignOrder(params.id);
      setOrder(updated);
    } finally {
      setAssigning(false);
    }
  }

  const isAssignedToMe = order?.sales_rep?.id === user?.id;
  const canEstimate =
    order?.status === "links_submitted" || order?.status === "price_changed";

  return (
    <RouteGuard allowedRoles={["sales_rep", "admin"]}>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-brand-violet px-4 py-3 flex items-center gap-4">
          <Link href="/dashboard" className="text-brand-pink-lightest text-sm hover:underline">
            ← Dashboard
          </Link>
          <h1 className="font-brielle text-xl text-white">Detalle del pedido</h1>
        </header>

        <main className="max-w-3xl mx-auto px-4 py-6 space-y-5">
          {loading && <p className="text-gray-400 text-center py-10">Cargando...</p>}

          {order && (
            <>
              {/* Header */}
              <div className="card">
                <div className="flex items-start justify-between gap-4 flex-wrap">
                  <div>
                    <h2 className="font-brielle text-2xl text-brand-violet">{order.order_number}</h2>
                    <p className="text-sm text-gray-400 mt-0.5">
                      {format(new Date(order.created_at), "d 'de' MMMM yyyy · HH:mm", { locale: es })}
                    </p>
                  </div>
                  <StatusBadge status={order.status} />
                </div>

                {/* Assignment */}
                <div className="mt-4 pt-4 border-t border-gray-100 flex items-center justify-between flex-wrap gap-3">
                  <div className="text-sm">
                    {order.sales_rep ? (
                      <span className="text-gray-600">
                        Asignado a:{" "}
                        <span className="font-semibold text-gray-800">
                          {order.sales_rep.full_name}
                          {isAssignedToMe && " (tú)"}
                        </span>
                      </span>
                    ) : (
                      <span className="text-gray-400">Sin asignar</span>
                    )}
                  </div>
                  {!order.sales_rep && (
                    <button
                      onClick={handleAssign}
                      disabled={assigning}
                      className="btn-primary text-sm py-1.5 disabled:opacity-60"
                    >
                      {assigning ? "Asignando..." : "Asignarme este pedido"}
                    </button>
                  )}
                  {canEstimate && (
                    <Link
                      href={`/dashboard/orders/${params.id}/estimate`}
                      className="btn-primary text-sm py-1.5 text-center"
                    >
                      Crear estimado
                    </Link>
                  )}
                </div>
              </div>

              {/* Customer info */}
              <div className="card text-sm space-y-1">
                <h3 className="font-semibold text-gray-800 mb-2">Cliente</h3>
                <p className="text-gray-700 font-medium">{order.customer.full_name}</p>
                <p className="text-gray-400">{order.customer.email}</p>
                {order.customer.phone && <p className="text-gray-400">{order.customer.phone}</p>}
                {order.customer.cuba_address && (
                  <p className="text-gray-400">
                    {order.customer.cuba_address}
                    {order.customer.cuba_city && `, ${order.customer.cuba_city}`}
                  </p>
                )}
              </div>

              {/* Products */}
              <div className="card space-y-4">
                <h3 className="font-semibold text-gray-800">
                  Productos ({order.items.length})
                </h3>
                {order.items.map((item, i) => (
                  <div key={item.id} className="border-t border-gray-100 pt-4 first:border-0 first:pt-0">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-semibold text-brand-violet mb-1">
                          Producto {i + 1}
                        </p>
                        <a
                          href={item.product_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-blue-600 hover:underline break-all"
                        >
                          {item.product_url}
                        </a>
                        <div className="flex flex-wrap gap-3 mt-1 text-xs text-gray-500">
                          <span>Cant: {item.quantity}</span>
                          {item.size && <span>Talla: {item.size}</span>}
                          {item.color && <span>Color: {item.color}</span>}
                          {item.variant_notes && <span>Notas: {item.variant_notes}</span>}
                        </div>
                      </div>
                      {item.price_at_estimate_usd != null && (
                        <span className="text-sm font-semibold text-gray-800 shrink-0">
                          ${item.price_at_estimate_usd.toFixed(2)}
                          {item.price_changed && (
                            <span className="ml-1 text-yellow-600 text-xs">⚠</span>
                          )}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              {/* Shipping */}
              {(order.shipping_method || order.delivery_preference) && (
                <div className="card text-sm space-y-1">
                  <h3 className="font-semibold text-gray-800 mb-2">Envío</h3>
                  {order.shipping_method && (
                    <p className="text-gray-600">
                      Modalidad: <span className="font-medium">{SHIPPING_LABELS[order.shipping_method]}</span>
                    </p>
                  )}
                  {order.delivery_preference && (
                    <p className="text-gray-600">
                      Entrega: <span className="font-medium">{DELIVERY_LABELS[order.delivery_preference]}</span>
                    </p>
                  )}
                  {order.tracking_number && (
                    <p className="text-gray-600">
                      Tracking: <span className="font-mono">{order.tracking_number}</span>
                    </p>
                  )}
                  {order.weight_kg != null && (
                    <p className="text-gray-600">Peso: {order.weight_kg} kg</p>
                  )}
                </div>
              )}

              {/* Financials */}
              {order.subtotal_usd != null && (
                <div className="card text-sm space-y-2">
                  <h3 className="font-semibold text-gray-800 mb-3">Costos</h3>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Subtotal</span>
                    <span>${order.subtotal_usd.toFixed(2)}</span>
                  </div>
                  {order.service_fee_usd != null && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">Servicio ({(order.service_fee_pct * 100).toFixed(0)}%)</span>
                      <span>${order.service_fee_usd.toFixed(2)}</span>
                    </div>
                  )}
                  {order.customs_estimate_usd != null && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">Aduana estimada</span>
                      <span>${order.customs_estimate_usd.toFixed(2)}</span>
                    </div>
                  )}
                  {order.shipping_charged_usd != null && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">Envío cobrado</span>
                      <span>${order.shipping_charged_usd.toFixed(2)}</span>
                    </div>
                  )}
                  <div className="flex justify-between font-semibold text-brand-violet border-t border-gray-100 pt-2">
                    <span>{order.total_final_usd != null ? "Total final" : "Estimado total"}</span>
                    <span>${(order.total_final_usd ?? order.total_estimate_usd ?? 0).toFixed(2)} USD</span>
                  </div>
                  {order.deposit_paid_usd != null && (
                    <div className="flex justify-between text-green-600">
                      <span>Depósito recibido ({order.deposit_payment_method})</span>
                      <span>− ${order.deposit_paid_usd.toFixed(2)}</span>
                    </div>
                  )}
                </div>
              )}

              {/* Customer notes */}
              {order.customer_notes && (
                <div className="card text-sm">
                  <h3 className="font-semibold text-gray-800 mb-1">Notas del cliente</h3>
                  <p className="text-gray-500">{order.customer_notes}</p>
                </div>
              )}

              {/* Status timeline */}
              <div className="card text-sm">
                <h3 className="font-semibold text-gray-800 mb-1">Estado actual</h3>
                <p className="text-gray-500">
                  {ORDER_STATUS_LABELS[order.status]} — MC-004 agregará el historial completo de estados.
                </p>
              </div>
            </>
          )}
        </main>
      </div>
    </RouteGuard>
  );
}
