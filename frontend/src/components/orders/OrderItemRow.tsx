"use client";

import { OrderItemInput } from "@/lib/api/orders";

interface Props {
  index: number;
  item: OrderItemInput;
  onChange: (index: number, updated: OrderItemInput) => void;
  onRemove: (index: number) => void;
  showRemove: boolean;
}

export default function OrderItemRow({ index, item, onChange, onRemove, showRemove }: Props) {
  function update(field: keyof OrderItemInput, value: string | number) {
    onChange(index, { ...item, [field]: value });
  }

  return (
    <div className="border border-gray-100 rounded-brand p-4 space-y-3 bg-gray-50">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-brand-violet uppercase tracking-wide">
          Producto {index + 1}
        </span>
        {showRemove && (
          <button
            type="button"
            onClick={() => onRemove(index)}
            className="text-xs text-red-400 hover:text-red-600"
          >
            Eliminar
          </button>
        )}
      </div>

      <div>
        <label className="block text-xs font-medium text-gray-600 mb-1">
          Enlace del producto <span className="text-red-500">*</span>
        </label>
        <input
          type="url"
          required
          value={item.product_url}
          onChange={(e) => update("product_url", e.target.value)}
          placeholder="https://www.amazon.com/dp/..."
          className="w-full border border-gray-200 rounded-brand px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-violet"
        />
      </div>

      <div className="grid grid-cols-3 gap-2">
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Cantidad</label>
          <input
            type="number"
            min={1}
            value={item.quantity}
            onChange={(e) => update("quantity", parseInt(e.target.value) || 1)}
            className="w-full border border-gray-200 rounded-brand px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-violet"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Talla</label>
          <input
            type="text"
            value={item.size ?? ""}
            onChange={(e) => update("size", e.target.value)}
            placeholder="M, L, 38..."
            className="w-full border border-gray-200 rounded-brand px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-violet"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Color</label>
          <input
            type="text"
            value={item.color ?? ""}
            onChange={(e) => update("color", e.target.value)}
            placeholder="Negro, Rojo..."
            className="w-full border border-gray-200 rounded-brand px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-violet"
          />
        </div>
      </div>

      <div>
        <label className="block text-xs font-medium text-gray-600 mb-1">Notas adicionales</label>
        <input
          type="text"
          value={item.variant_notes ?? ""}
          onChange={(e) => update("variant_notes", e.target.value)}
          placeholder="Ej: versión sin logo, con caja..."
          className="w-full border border-gray-200 rounded-brand px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-violet"
        />
      </div>
    </div>
  );
}
