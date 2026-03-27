import { create } from "zustand";
import { persist } from "zustand/middleware";
import { User } from "@/types";
import { api } from "@/lib/api";

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  fetchMe: () => Promise<void>;
}

interface RegisterData {
  full_name: string;
  email: string;
  password: string;
  phone?: string;
  cuba_address?: string;
  cuba_city?: string;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isLoading: false,

      login: async (email, password) => {
        set({ isLoading: true });
        try {
          const res = await api.post("/auth/login", { email, password });
          const { access_token, user } = res.data;
          localStorage.setItem("access_token", access_token);
          set({ token: access_token, user, isLoading: false });
        } catch (err) {
          set({ isLoading: false });
          throw err;
        }
      },

      register: async (data) => {
        set({ isLoading: true });
        try {
          const res = await api.post("/auth/register", data);
          const { access_token, user } = res.data;
          localStorage.setItem("access_token", access_token);
          set({ token: access_token, user, isLoading: false });
        } catch (err) {
          set({ isLoading: false });
          throw err;
        }
      },

      logout: () => {
        localStorage.removeItem("access_token");
        set({ user: null, token: null });
      },

      fetchMe: async () => {
        try {
          const res = await api.get("/auth/me");
          set({ user: res.data });
        } catch {
          set({ user: null, token: null });
          localStorage.removeItem("access_token");
        }
      },
    }),
    {
      name: "micloset-auth",
      partialize: (state) => ({ token: state.token, user: state.user }),
    }
  )
);
