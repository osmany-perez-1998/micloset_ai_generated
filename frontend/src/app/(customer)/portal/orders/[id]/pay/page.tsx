"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import RouteGuard from "@/components/layout/RouteGuard";
import { getOrder, recordPayment } from "@/lib/api/orders";
import { Order } from "@/types";

export default function PaymentPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [order, setOrder] = useState<Order | null>(null);
  const [paymentType, setPaymentType] = useState<"deposit" | "full_prepay">("deposit");
  const [paymentMethod, setPaymentMethod] = useState<"cash" | "wire_transfer">("cash");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    getOrder(params.id)
      .then(setOrder)
      .catch(() => setError("No se pudo cargar el pedido."));
  }, [params.id]);

  const total = order?.total_estimate_usd ?? 0;
  const depositAmount = total * 0.5;
  const amountDue = paymentType === "deposit" ? depositAmount : total;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await recordPayment(params.id, {
        payment_type: paymentType,
        amount_usd: parseFloat(amountDue.toFixed(2)),
        payment_method: paymentMethod,
      });
      router.push(`/portal/orders/${params.id}`);
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Error al registrar el pago.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <RouteGuard allowedRoles={["customer"]}>
      <div className="min-h-screen bg-brand-pink-lightest">
        <header className="bg-brand-violet px-6 py-4 flex items-center gap-4">
          <Link
            href={`/portal/orders/${params.id}`}
            className="text-brand-pink-lightest text-sm hover:underline"
          >
            ← Pedido
          </Link>
          <h1 className="font-brielle text-2xl text-white">Mi Closet</h1>
        </header>

        <main className="max-w-md mx-auto px-4 py-8 space-y-6">
          {error && !order && (
            <p className="text-red-500 text-center py-10">{error}</p>
          )}

          {order && (
            <>
              {/* Order summary */}
              <div className="card space-y-2 text-sm">
                <h2 className="font-brielle text-xl text-brand-violet mb-3">
                  Estimado recibido
                </h2>
                <p className="text-gray-500 font-mono text-xs">{order.order_number}</p>

                {order.subtotal_usd != null && (
                  <>
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
                    <div className="flex justify-between font-semibold text-brand-violet border-t border-gray-100 pt-2">
                      <span>Total estimado</span>
                      <span>${total.toFixed(2)} USD</span>
                    </div>
                  </>
                )}

                <p className="text-xs text-gray-400 pt-1">
                  El costo de envío se calculará cuando los productos lleguen a Miami y se añadirá al pago final.
                </p>
              </div>

              {/* Payment form */}
              <form onSubmit={handleSubmit} className="space-y-5">
                {/* Payment type */}
                <div className="card space-y-3">
                  <h3 className="font-semibold text-gray-800">¿Cuánto deseas pagar ahora?</h3>

                  <label className={`flex items-start gap-3 p-3 rounded-xl border-2 cursor-pointer transition-colors ${paymentType === "deposit" ? "border-brand-violet bg-brand-violet/5" : "border-gray-200"}`}>
                    <input
                      type="radio"
                      name="payment_type"
                      value="deposit"
                      checked={paymentType === "deposit"}
                      onChange={() => setPaymentType("deposit")}
                      className="mt-0.5 accent-brand-violet"
                    />
                    <div>
                      <p className="font-medium text-gray-800">
                        Depósito — ${depositAmount.toFixed(2)} USD
                      </p>
                      <p className="text-xs text-gray-400">
                        50% ahora. El resto más envío se paga al llegar a Cuba.
                      </p>
                    </div>
                  </label>

                  <label className={`flex items-start gap-3 p-3 rounded-xl border-2 cursor-pointer transition-colors ${paymentType === "full_prepay" ? "border-brand-violet bg-brand-violet/5" : "border-gray-200"}`}>
                    <input
                      type="radio"
                      name="payment_type"
                      value="full_prepay"
                      checked={paymentType === "full_prepay"}
                      onChange={() => setPaymentType("full_prepay")}
                      className="mt-0.5 accent-brand-violet"
                    />
                    <div>
                      <p className="font-medium text-gray-800">
                        Pago completo — ${total.toFixed(2)} USD
                      </p>
                      <p className="text-xs text-gray-400">
                        100% del estimado. Solo queda pendiente el flete de Miami a Cuba.
                      </p>
                    </div>
                  </label>
                </div>

                {/* Payment method */}
                <div className="card space-y-3">
                  <h3 className="font-semibold text-gray-800">Método de pago</h3>

                  <label className={`flex items-center gap-3 p-3 rounded-xl border-2 cursor-pointer transition-colors ${paymentMethod === "cash" ? "border-brand-violet bg-brand-violet/5" : "border-gray-200"}`}>
                    <input
                      type="radio"
                      name="payment_method"
                      value="cash"
                      checked={paymentMethod === "cash"}
                      onChange={() => setPaymentMethod("cash")}
                      className="accent-brand-violet"
                    />
                    <span className="font-medium text-gray-800">Efectivo</span>
                  </label>

                  <label className={`flex items-center gap-3 p-3 rounded-xl border-2 cursor-pointer transition-colors ${paymentMethod === "wire_transfer" ? "border-brand-violet bg-brand-violet/5" : "border-gray-200"}`}>
                    <input
                      type="radio"
                      name="payment_method"
                      value="wire_transfer"
                      checked={paymentMethod === "wire_transfer"}
                      onChange={() => setPaymentMethod("wire_transfer")}
                      className="accent-brand-violet"
                    />
                    <span className="font-medium text-gray-800">Transferencia bancaria</span>
                  </label>
                </div>

                {/* Confirmation */}
                <div className="card bg-brand-violet/5 border border-brand-violet/20 text-sm space-y-1">
                  <p className="text-gray-700">
                    Al confirmar, aceptas el estimado y autorizas la compra de tus productos.
                  </p>
                  <p className="font-semibold text-brand-violet text-base mt-1">
                    A pagar: ${amountDue.toFixed(2)} USD
                  </p>
                </div>

                {error && (
                  <p className="text-red-500 text-sm text-center">{error}</p>
                )}

                <button
                  type="submit"
                  disabled={submitting}
                  className="btn-primary w-full disabled:opacity-60"
                >
                  {submitting ? "Procesando..." : `Confirmar pago de $${amountDue.toFixed(2)} USD`}
                </button>
              </form>
            </>
          )}
        </main>
      </div>
    </RouteGuard>
  );
}
