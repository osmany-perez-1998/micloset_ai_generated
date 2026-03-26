/**
 * MiCloset Brand Design System
 * Source: Manual de Identidad Visual - Mi Closet
 */

export const colors = {
  purple: "#904cd8",
  blue: "#2656dd",
  pink: "#ea7db7",
  purpleLight: "#a170e0",
  purpleLighter: "#b892e8",
  blueLight: "#4c6ee5",
  blueLighter: "#6e8ee5",
  pinkLight: "#edb4d2",
  pinkLightest: "#f6d5e5",
  black: "#000000",
  white: "#ffffff",
  gray: {
    50: "#fafafa",
    100: "#f5f5f5",
    200: "#e5e5e5",
    300: "#d4d4d4",
    400: "#a3a3a3",
    500: "#737373",
    600: "#525252",
    700: "#404040",
    800: "#262626",
    900: "#171717",
  },
} as const;

export const fonts = {
  heading: "'Brielle', serif",
  body: "'Montserrat', sans-serif",
  logo: "'Comfortaa', cursive",
} as const;

export const ORDER_STATUSES = [
  { key: "SUBMITTED",           label: "Order Submitted",     icon: "📋" },
  { key: "ESTIMATED",           label: "Estimate Ready",      icon: "💰" },
  { key: "AWAITING_DEPOSIT",    label: "Awaiting Deposit",    icon: "⏳" },
  { key: "DEPOSIT_RECEIVED",    label: "Deposit Received",    icon: "✅" },
  { key: "PRICE_VERIFICATION",  label: "Verifying Prices",    icon: "🔍" },
  { key: "PURCHASING",          label: "Purchasing Items",    icon: "🛒" },
  { key: "SHIPPED_TO_MIAMI",    label: "Shipped to Miami",    icon: "✈️" },
  { key: "RECEIVED_IN_MIAMI",   label: "Received in Miami",   icon: "📦" },
  { key: "IN_TRANSIT_TO_CUBA",  label: "In Transit to Cuba",  icon: "🚢" },
  { key: "RECEIVED_IN_CUBA",    label: "Arrived in Cuba",     icon: "🇨🇺" },
  { key: "CATEGORIZING",        label: "Sorting Your Items",  icon: "📂" },
  { key: "FINAL_INVOICE_SENT",  label: "Final Invoice Sent",  icon: "📄" },
  { key: "COMPLETED",           label: "Delivered",           icon: "🎉" },
  { key: "CANCELLED",           label: "Cancelled",           icon: "❌" },
] as const;

export type OrderStatusKey = typeof ORDER_STATUSES[number]["key"];
