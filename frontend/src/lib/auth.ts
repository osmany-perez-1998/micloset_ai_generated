"use client";

export interface AuthUser {
  id: number;
  phone: string;
  name: string;
  role: "CUSTOMER" | "SALES_REP" | "ADMIN";
  address_cuba: string | null;
  province_cuba: string | null;
}

export function saveAuth(accessToken: string, refreshToken: string, user: AuthUser): void {
  localStorage.setItem("mc_access_token", accessToken);
  localStorage.setItem("mc_refresh_token", refreshToken);
  localStorage.setItem("mc_user", JSON.stringify(user));
}

export function clearAuth(): void {
  localStorage.removeItem("mc_access_token");
  localStorage.removeItem("mc_refresh_token");
  localStorage.removeItem("mc_user");
}

export function getStoredUser(): AuthUser | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem("mc_user");
  if (!raw) return null;
  try {
    return JSON.parse(raw) as AuthUser;
  } catch {
    return null;
  }
}

export function isLoggedIn(): boolean {
  if (typeof window === "undefined") return false;
  return !!localStorage.getItem("mc_access_token");
}

export interface CartItem {
  id: string;
  product_url: string;
  quantity: number;
  notes?: string;
  variant?: string;
  estimated_price?: number;
  product_name?: string;
  product_image_url?: string;
}

export function getCart(): CartItem[] {
  if (typeof window === "undefined") return [];
  try {
    return JSON.parse(localStorage.getItem("mc_cart") || "[]");
  } catch {
    return [];
  }
}

export function saveCart(items: CartItem[]): void {
  localStorage.setItem("mc_cart", JSON.stringify(items));
}

export function clearCart(): void {
  localStorage.removeItem("mc_cart");
}
