import RouteGuard from "@/components/layout/RouteGuard";
import NewOrderForm from "@/components/orders/NewOrderForm";

export default function NewOrderPage() {
  return (
    <RouteGuard allowedRoles={["customer"]}>
      <div className="min-h-screen bg-brand-pink-lightest">
        <header className="bg-brand-violet px-6 py-4">
          <h1 className="font-brielle text-2xl text-white">Mi Closet</h1>
        </header>

        <main className="max-w-2xl mx-auto px-4 py-8">
          <div className="mb-6">
            <h2 className="font-brielle text-2xl text-brand-violet">Nuevo Pedido</h2>
            <p className="text-gray-500 text-sm mt-1">
              Pega los enlaces de los productos que deseas pedir.
            </p>
          </div>
          <div className="card">
            <NewOrderForm />
          </div>
        </main>
      </div>
    </RouteGuard>
  );
}
