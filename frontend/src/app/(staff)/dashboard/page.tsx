import RouteGuard from "@/components/layout/RouteGuard";

export default function SalesRepDashboard() {
  return (
    <RouteGuard allowedRoles={["sales_rep", "admin"]}>
      <main className="min-h-screen bg-white p-8">
        <h1 className="font-brielle text-3xl text-brand-violet">Dashboard</h1>
        <p className="text-gray-500 mt-2">Panel de ventas — MC-003 coming next.</p>
      </main>
    </RouteGuard>
  );
}
