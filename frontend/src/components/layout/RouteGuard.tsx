"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/store/auth";
import { UserRole } from "@/types";

interface RouteGuardProps {
  children: React.ReactNode;
  allowedRoles?: UserRole[];
}

/**
 * Wraps any page that requires authentication.
 * Optionally restricts to specific roles (e.g. sales_rep, admin).
 *
 * Usage:
 *   <RouteGuard>...</RouteGuard>                          // any logged-in user
 *   <RouteGuard allowedRoles={["sales_rep","admin"]}>...  // staff only
 */
export default function RouteGuard({ children, allowedRoles }: RouteGuardProps) {
  const { user, token } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    if (!token || !user) {
      router.replace("/login");
      return;
    }
    if (allowedRoles && !allowedRoles.includes(user.role)) {
      // Wrong role — send them to their correct home
      if (user.role === "customer") router.replace("/portal");
      else router.replace("/dashboard");
    }
  }, [token, user, allowedRoles, router]);

  if (!token || !user) return null;
  if (allowedRoles && !allowedRoles.includes(user.role)) return null;

  return <>{children}</>;
}
