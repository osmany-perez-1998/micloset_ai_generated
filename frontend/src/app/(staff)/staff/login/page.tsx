"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/store/auth";

export default function StaffLoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { login, isLoading } = useAuthStore();
  const router = useRouter();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      await login(email, password);
      const user = useAuthStore.getState().user;
      if (user?.role !== "sales_rep" && user?.role !== "admin") {
        useAuthStore.getState().logout();
        setError("Esta área es solo para el equipo de Mi Closet.");
        return;
      }
      router.push("/dashboard");
    } catch {
      setError("Correo o contraseña incorrectos.");
    }
  }

  return (
    <div className="min-h-screen bg-brand-violet flex items-center justify-center px-4">
      <div className="card w-full max-w-sm">
        {/* Logo */}
        <div className="text-center mb-8">
          <h1 className="font-brielle text-4xl text-brand-violet">Mi Closet</h1>
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mt-1">
            Portal del equipo
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Correo electrónico
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full border border-gray-200 rounded-brand px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-violet"
              placeholder="rep@micloset.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Contraseña
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border border-gray-200 rounded-brand px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-violet"
              placeholder="••••••••"
            />
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
            {isLoading ? "Entrando..." : "Entrar"}
          </button>
        </form>
      </div>
    </div>
  );
}
