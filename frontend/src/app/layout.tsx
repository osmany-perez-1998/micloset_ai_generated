import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Mi Closet — Shopping from the US to Cuba",
  description:
    "Order products from any US website. We handle purchasing, shipping, and delivery to Cuba.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-white antialiased">{children}</body>
    </html>
  );
}
