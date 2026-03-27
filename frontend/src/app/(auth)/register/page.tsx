"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuthStore } from "@/lib/store/auth";

export default function RegisterPage() {
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
    phone: "",
    cuba_address: "",
    cuba_city: "",
  });
  const [error, setError] = useState("");
  const { register, isLoading } = useAuthStore();
  const router = useRouter();

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      await register(form);
      router.push("/portal");
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Error al registrarse. Intenta de nuevo.";
      setError(message);
    }
  }

  const field = (
    label: string,
    name: keyof typeof form,
    type = "text",
    placeholder = "",
    required = false
  ) => (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      <input
        type={type}
        name={name}
        required={required}
        value={form[name]}
        onChange={handleChange}
        placeholder={placeholder}
        className="w-full border border-gray-200 rounded-brand px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-violet"
      />
    </div>
  );

  return (
    <div className="min-h-screen bg-brand-pink-lightest flex items-center justify-center px-4 py-10">
      <div className="card w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="font-brielle text-4xl text-brand-violet">Mi Closet</h1>
          <p className="font-sans text-gray-500 text-sm mt-1">Crea tu cuenta</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {field("Nombre completo", "full_name", "text", "Ana García", true)}
          {field("Correo electrónico", "email", "email", "tu@correo.com", true)}
          {field("Contraseña", "password", "password", "••••••••", true)}
          {field("Teléfono (opcional)", "phone", "tel", "+5351234567")}

          <div className="border-t border-gray-100 pt-4">
            <p className="text-xs text-gray-400 mb-3">Dirección de entrega en Cuba (opcional)</p>
            {field("Dirección", "cuba_address", "text", "Calle 23 #456, Vedado")}
            {field("Ciudad / Municipio", "cuba_city", "text", "La Habana")}
          </div>

          {error && (
            <p className="text-red-600 text-sm bg-red-50 border border-red-200 rounded-brand px-4 py-2">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="btn-primary w-full disabled:opacity-60"
          >
            {isLoading ? "Creando cuenta..." : "Crear cuenta"}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-6">
          ¿Ya tienes cuenta?{" "}
          <Link href="/login" className="text-brand-violet font-semibold hover:underline">
            Inicia sesión
          </Link>
        </p>
      </div>
    </div>
  );
}
