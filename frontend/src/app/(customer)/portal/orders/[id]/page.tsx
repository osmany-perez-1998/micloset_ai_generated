"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { format } from "date-fns";
import { es } from "date-fns/locale";
import RouteGuard from "@/components/layout/RouteGuard";
import StatusBadge from "@/components/orders/StatusBadge";
import { getOrder } from "@/lib/api/orders";
import { Order } from "@/types";

const SHIPPING_LABELS: Record<string, string> = {
  express_air: "Aéreo Express",
  standard_air: "Aéreo Estándar",
  maritime: "Marítimo",
};

const DELIVERY_LABELS: Record<string, string> = {
  home_delivery: "Entrega a domicilio",
  pickup: "Recoger en punto",
};

export default function OrderDetailPage({ params }: { params: { id: string } }) {
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getOrder(params.id)
      .then(setOrder)
      .catch(() => setError("No se pudo cargar el pedido."))
      .finally(() => setLoading(false));
  }, [params.id]);

  return (
    <RouteGuard allowedRoles={["customer"]}>
      <div className="min-h-screen bg-brand-pink-lightest">
        <header className="bg-brand-violet px-6 py-4 flex items-center gap-4">
          <Link href="/portal" className="text-brand-pink-lightest text-sm hover:underline">
            ← Mis pedidos
          </Link>
          <h1 className="font-brielle text-2xl text-white">Mi Closet</h1>
        </header>

        <main className="max-w-2xl mx-auto px-4 py-8 space-y-6">
          {loading && <p className="text-gray-400 text-center py-10">Cargando...</p>}
          {error && <p className="text-red-500 text-center py-10">{error}</p>}

          {order && (
            <>
              {/* Header card */}
              <div className="card space-y-3">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h2 className="font-brielle text-2xl text-brand-violet">{order.order_number}</h2>
                    <p className="text-sm text-gray-400 mt-0.5">
                      {format(new Date(order.created_at), "d 'de' MMMM yyyy", { locale: es })}
                    </p>
                  </div>
                  <StatusBadge status={order.status} />
                </div>
                {order.status === "estimate_provided" && (
                  <Link
                    href={`/portal/orders/${params.id}/pay`}
                    className="btn-primary block text-center w-full"
                  >
                    Ver estimado y confirmar pago
                  </Link>
                )}
              </div>

              {/* Products */}
              <div className="card space-y-3">
                <h3 className="font-semibold text-gray-800">
                  Productos ({order.items.length})
                </h3>
                {order.items.map((item, i) => (
                  <div key={item.id} className="border-t border-gray-100 pt-3 first:border-0 first:pt-0">
                    <p className="text-xs text-brand-violet font-semibold mb-1">
                      Producto {i + 1}
                    </p>
                    <a
                      href={item.product_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:underline break-all"
                    >
                      {item.product_name ?? item.product_url}
                    </a>
                    <div className="flex gap-3 mt-1 text-xs text-gray-500">
                      <span>Cant: {item.quantity}</span>
                      {item.size && <span>Talla: {item.size}</span>}
                      {item.color && <span>Color: {item.color}</span>}
                    </div>
                    {item.price_at_estimate_usd != null && (
                      <p className="text-sm font-medium text-gray-700 mt-1">
                        ${item.price_at_estimate_usd.toFixed(2)} USD
                        {item.price_changed && (
                          <span className="ml-2 text-yellow-600 text-xs">⚠ Precio cambió</span>
                        )}
                      </p>
                    )}
                  </div>
                ))}
              </div>

              {/* Price breakdown */}
              {order.subtotal_usd != null && (
                <div className="card space-y-2 text-sm">
                  <h3 className="font-semibold text-gray-800 mb-3">Resumen de costos</h3>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Subtotal productos</span>
                    <span>${order.subtotal_usd.toFixed(2)}</span>
                  </div>
                  {order.service_fee_usd != null && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">
                        Servicio ({(order.service_fee_pct * 100).toFixed(0)}%)
                      </span>
                      <span>${order.service_fee_usd.toFixed(2)}</span>
                    </div>
                  )}
                  {order.customs_estimate_usd != null && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">Estimado aduana</span>
                      <span>${order.customs_estimate_usd.toFixed(2)}</span>
                    </div>
                  )}
                  {order.shipping_charged_usd != null && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">Envío</span>
                      <span>${order.shipping_charged_usd.toFixed(2)}</span>
                    </div>
                  )}
                  <div className="flex justify-between font-semibold text-brand-violet border-t border-gray-100 pt-2 mt-2">
                    <span>{order.total_final_usd != null ? "Total final" : "Estimado total"}</span>
                    <span>
                      ${(order.total_final_usd ?? order.total_estimate_usd ?? 0).toFixed(2)} USD
                    </span>
                  </div>
                  {order.deposit_paid_usd != null && (
                    <div className="flex justify-between text-green-600">
                      <span>Depósito pagado</span>
                      <span>− ${order.deposit_paid_usd.toFixed(2)}</span>
                    </div>
                  )}
                </div>
              )}

              {/* Shipping info */}
              {(order.shipping_method || order.delivery_preference) && (
                <div className="card text-sm space-y-1">
                  <h3 className="font-semibold text-gray-800 mb-2">Envío</h3>
                  {order.shipping_method && (
                    <p className="text-gray-500">
                      Modalidad:{" "}
                      <span className="text-gray-800">{SHIPPING_LABELS[order.shipping_method]}</span>
                    </p>
                  )}
                  {order.delivery_preference && (
                    <p className="text-gray-500">
                      Entrega:{" "}
                      <span className="text-gray-800">{DELIVERY_LABELS[order.delivery_preference]}</span>
                    </p>
                  )}
                  {order.tracking_number && (
                    <p className="text-gray-500">
                      Tracking: <span className="font-mono text-gray-800">{order.tracking_number}</span>
                    </p>
                  )}
                </div>
              )}

              {order.customer_notes && (
                <div className="card text-sm">
                  <h3 className="font-semibold text-gray-800 mb-1">Notas</h3>
                  <p className="text-gray-500">{order.customer_notes}</p>
                </div>
              )}
            </>
          )}
        </main>
      </div>
    </RouteGuard>
  );
}
