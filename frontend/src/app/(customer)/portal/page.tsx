import RouteGuard from "@/components/layout/RouteGuard";

export default function CustomerPortal() {
  return (
    <RouteGuard allowedRoles={["customer"]}>
      <main className="min-h-screen bg-brand-pink-lightest p-8">
        <h1 className="font-brielle text-3xl text-brand-violet">Mi Portal</h1>
        <p className="text-gray-500 mt-2">Bienvenido a Mi Closet — MC-002 coming next.</p>
      </main>
    </RouteGuard>
  );
}
