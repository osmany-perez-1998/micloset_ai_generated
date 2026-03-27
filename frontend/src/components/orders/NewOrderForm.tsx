"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createOrder, OrderItemInput } from "@/lib/api/orders";
import OrderItemRow from "./OrderItemRow";

const emptyItem = (): OrderItemInput => ({
  product_url: "",
  quantity: 1,
});

export default function NewOrderForm() {
  const [items, setItems] = useState<OrderItemInput[]>([emptyItem()]);
  const [shippingMethod, setShippingMethod] = useState("");
  const [deliveryPreference, setDeliveryPreference] = useState("");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  function updateItem(index: number, updated: OrderItemInput) {
    setItems((prev) => prev.map((it, i) => (i === index ? updated : it)));
  }

  function removeItem(index: number) {
    setItems((prev) => prev.filter((_, i) => i !== index));
  }

  function addItem() {
    setItems((prev) => [...prev, emptyItem()]);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const order = await createOrder({
        items,
        shipping_method: shippingMethod || undefined,
        delivery_preference: deliveryPreference || undefined,
        customer_notes: notes || undefined,
      });
      router.push(`/portal/orders/${order.id}`);
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Error al crear el pedido. Intenta de nuevo.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Items */}
      <div className="space-y-3">
        {items.map((item, i) => (
          <OrderItemRow
            key={i}
            index={i}
            item={item}
            onChange={updateItem}
            onRemove={removeItem}
            showRemove={items.length > 1}
          />
        ))}
        <button
          type="button"
          onClick={addItem}
          className="btn-secondary w-full text-sm"
        >
          + Agregar otro producto
        </button>
      </div>

      {/* Shipping options */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Tipo de envío
          </label>
          <select
            value={shippingMethod}
            onChange={(e) => setShippingMethod(e.target.value)}
            className="w-full border border-gray-200 rounded-brand px-3 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-violet bg-white"
          >
            <option value="">Por definir</option>
            <option value="express_air">Aéreo Express</option>
            <option value="standard_air">Aéreo Estándar</option>
            <option value="maritime">Marítimo</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Forma de entrega
          </label>
          <select
            value={deliveryPreference}
            onChange={(e) => setDeliveryPreference(e.target.value)}
            className="w-full border border-gray-200 rounded-brand px-3 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-violet bg-white"
          >
            <option value="">Por definir</option>
            <option value="home_delivery">Entrega a domicilio</option>
            <option value="pickup">Recoger en punto</option>
          </select>
        </div>
      </div>

      {/* Notes */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Notas para el pedido
        </label>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          rows={3}
          placeholder="Cualquier detalle adicional para tu pedido..."
          className="w-full border border-gray-200 rounded-brand px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-violet resize-none"
        />
      </div>

      {error && (
        <p className="text-red-600 text-sm bg-red-50 border border-red-200 rounded-brand px-4 py-2">
          {error}
        </p>
      )}

      <button
        type="submit"
        disabled={loading}
        className="btn-primary w-full disabled:opacity-60"
      >
        {loading ? "Enviando pedido..." : "Enviar pedido"}
      </button>
    </form>
  );
}
