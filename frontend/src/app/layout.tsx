import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Mi Closet",
  description: "Tu tienda online desde Estados Unidos a Cuba",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
