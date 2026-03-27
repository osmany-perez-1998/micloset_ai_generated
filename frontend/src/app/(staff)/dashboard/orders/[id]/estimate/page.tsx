"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import RouteGuard from "@/components/layout/RouteGuard";
import { getOrder } from "@/lib/api/orders";
import {
  fetchPrices,
  submitEstimate,
  PriceFetchResult,
} from "@/lib/api/staff";
import { Order, OrderItem } from "@/types";

const SERVICE_FEES = [0, 7, 10, 15, 17, 20];

interface ItemRow {
  item: OrderItem;
  fetched: PriceFetchResult | null;
  confirmedPrice: string; // string so user can edit freely
}

export default function EstimatePage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [order, setOrder] = useState<Order | null>(null);
  const [rows, setRows] = useState<ItemRow[]>([]);
  const [feePct, setFeePct] = useState<number>(10);
  const [fetching, setFetching] = useState(false);
  const [fetchDone, setFetchDone] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    getOrder(params.id).then((o) => {
      setOrder(o);
      setRows(
        o.items.map((item) => ({
          item,
          fetched: null,
          confirmedPrice: "",
        }))
      );
    });
  }, [params.id]);

  async function handleFetchPrices() {
    setFetching(true);
    setError("");
    try {
      const result = await fetchPrices(params.id);
      setRows((prev) =>
        prev.map((row) => {
          const fetched =
            result.results.find((r) => r.order_item_id === row.item.id) ?? null;
          return {
            ...row,
            fetched,
            confirmedPrice:
              fetched && fetched.price != null
                ? fetched.price.toFixed(2)
                : row.confirmedPrice,
          };
        })
      );
      setFetchDone(true);
    } catch {
      setError("Error al obtener precios. Intenta de nuevo.");
    } finally {
      setFetching(false);
    }
  }

  function updatePrice(itemId: string, val: string) {
    setRows((prev) =>
      prev.map((r) =>
        r.item.id === itemId ? { ...r, confirmedPrice: val } : r
      )
    );
  }

  const subtotal = rows.reduce((sum, r) => {
    const price = parseFloat(r.confirmedPrice) || 0;
    return sum + price * r.item.quantity;
  }, 0);
  const feeAmount = subtotal * (feePct / 100);
  const total = subtotal + feeAmount;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");

    for (const r of rows) {
      const p = parseFloat(r.confirmedPrice);
      if (!r.confirmedPrice || isNaN(p) || p <= 0) {
        setError(`Ingresa un precio válido para todos los productos.`);
        return;
      }
    }

    setSubmitting(true);
    try {
      await submitEstimate(params.id, {
        item_prices: rows.map((r) => ({
          order_item_id: r.item.id,
          price_usd: parseFloat(r.confirmedPrice),
        })),
        service_fee_pct: feePct,
      });
      router.push(`/dashboard/orders/${params.id}`);
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Error al enviar el estimado.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <RouteGuard allowedRoles={["sales_rep", "admin"]}>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-brand-violet px-4 py-3 flex items-center gap-4">
          <Link
            href={`/dashboard/orders/${params.id}`}
            className="text-brand-pink-lightest text-sm hover:underline"
          >
            ← Pedido
          </Link>
          <h1 className="font-brielle text-xl text-white">Crear estimado</h1>
          {order && (
            <span className="ml-auto text-brand-pink-lightest text-sm font-mono">
              {order.order_number}
            </span>
          )}
        </header>

        <main className="max-w-2xl mx-auto px-4 py-6 space-y-5">
          {/* Step 1 — Fetch prices */}
          <div className="card space-y-4">
            <div className="flex items-center justify-between flex-wrap gap-3">
              <h2 className="font-semibold text-gray-800">
                Paso 1 — Obtener precios automáticamente
              </h2>
              <button
                type="button"
                onClick={handleFetchPrices}
                disabled={fetching || !order}
                className="btn-primary text-sm py-1.5 disabled:opacity-60"
              >
                {fetching ? "Buscando precios..." : fetchDone ? "Actualizar precios" : "Obtener precios"}
              </button>
            </div>
            <p className="text-xs text-gray-400">
              El sistema intentará extraer el precio actual de cada enlace
              automáticamente. Si falla, ingresa el precio manualmente.
            </p>
          </div>

          {/* Products table */}
          {order && (
            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="card space-y-4">
                <h2 className="font-semibold text-gray-800">
                  Paso 2 — Confirmar precios por unidad
                </h2>

                {rows.map((row, i) => {
                  const methodLabel: Record<string, string> = {
                    "json-ld": "JSON-LD",
                    meta: "Meta tags",
                    css: "CSS selector",
                    openai: "OpenAI",
                  };
                  return (
                    <div
                      key={row.item.id}
                      className="border-t border-gray-100 pt-4 first:border-0 first:pt-0"
                    >
                      <div className="flex items-start gap-3">
                        <div className="flex-1 min-w-0">
                          <p className="text-xs font-semibold text-brand-violet mb-0.5">
                            Producto {i + 1} · cant. {row.item.quantity}
                          </p>
                          <a
                            href={row.item.product_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-blue-600 hover:underline break-all"
                          >
                            {row.item.product_url}
                          </a>
                          {row.item.size && (
                            <span className="ml-2 text-xs text-gray-400">
                              Talla: {row.item.size}
                            </span>
                          )}
                          {row.item.color && (
                            <span className="ml-2 text-xs text-gray-400">
                              Color: {row.item.color}
                            </span>
                          )}
                        </div>

                        {/* Price input */}
                        <div className="shrink-0 w-32">
                          {row.fetched && !row.fetched.needs_manual && (
                            <p className="text-xs text-green-600 mb-1">
                              Auto ({methodLabel[row.fetched.method ?? ""] ?? row.fetched.method})
                            </p>
                          )}
                          {row.fetched?.needs_manual && (
                            <p className="text-xs text-yellow-600 mb-1">
                              Manual requerido
                            </p>
                          )}
                          <div className="flex items-center border rounded-lg overflow-hidden focus-within:ring-2 focus-within:ring-brand-violet">
                            <span className="px-2 text-sm text-gray-400 bg-gray-50">$</span>
                            <input
                              type="number"
                              step="0.01"
                              min="0.01"
                              value={row.confirmedPrice}
                              onChange={(e) => updatePrice(row.item.id, e.target.value)}
                              placeholder="0.00"
                              className="w-full px-2 py-1.5 text-sm outline-none"
                            />
                          </div>
                          {row.confirmedPrice && row.item.quantity > 1 && (
                            <p className="text-xs text-gray-400 mt-0.5 text-right">
                              Total: ${(parseFloat(row.confirmedPrice) * row.item.quantity).toFixed(2)}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Fee selector */}
              <div className="card space-y-3">
                <h2 className="font-semibold text-gray-800">
                  Paso 3 — Tarifa de servicio
                </h2>
                <div className="flex flex-wrap gap-2">
                  {SERVICE_FEES.map((fee) => (
                    <button
                      key={fee}
                      type="button"
                      onClick={() => setFeePct(fee)}
                      className={`px-4 py-2 rounded-full text-sm font-medium border transition-colors ${
                        feePct === fee
                          ? "bg-brand-violet text-white border-brand-violet"
                          : "bg-white text-gray-700 border-gray-300 hover:border-brand-violet"
                      }`}
                    >
                      {fee === 0 ? "Sin cargo" : `${fee}%`}
                    </button>
                  ))}
                </div>
              </div>

              {/* Summary */}
              <div className="card space-y-2 text-sm">
                <h2 className="font-semibold text-gray-800 mb-3">Resumen del estimado</h2>
                <div className="flex justify-between">
                  <span className="text-gray-500">Subtotal productos</span>
                  <span>${subtotal.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">
                    Servicio {feePct > 0 ? `(${feePct}%)` : ""}
                  </span>
                  <span>${feeAmount.toFixed(2)}</span>
                </div>
                <div className="flex justify-between font-semibold text-brand-violet border-t border-gray-100 pt-2">
                  <span>Total estimado</span>
                  <span>${total.toFixed(2)} USD</span>
                </div>
                <div className="flex justify-between text-gray-400">
                  <span>Depósito requerido (50%)</span>
                  <span>${(total * 0.5).toFixed(2)} USD</span>
                </div>
              </div>

              {error && (
                <p className="text-red-500 text-sm text-center">{error}</p>
              )}

              <button
                type="submit"
                disabled={submitting || rows.length === 0}
                className="btn-primary w-full disabled:opacity-60"
              >
                {submitting ? "Enviando estimado..." : "Confirmar y enviar estimado al cliente"}
              </button>
            </form>
          )}
        </main>
      </div>
    </RouteGuard>
  );
}
