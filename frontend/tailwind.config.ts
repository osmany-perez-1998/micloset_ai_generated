import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      // ─── MiCloset Brand Tokens ───────────────────────────────────────────────
      colors: {
        brand: {
          // Violet — primary, power, luxury, creativity
          violet: {
            DEFAULT: "#904cd8",
            light: "#a170e0",
            lighter: "#b892e8",
          },
          // Blue — secondary, stability, trust
          blue: {
            DEFAULT: "#2656dd",
            light: "#4c6ee5",
            lighter: "#6e8ee5",
          },
          // Pink — secondary, emotional, passionate
          pink: {
            DEFAULT: "#ea7db7",
            light: "#edb4d2",
            lightest: "#f6d5e5",
          },
        },
      },
      fontFamily: {
        // Brielle — headlines (loaded via @font-face or CDN)
        brielle: ["Brielle", "Georgia", "serif"],
        // Montserrat — body text
        sans: ["Montserrat", "system-ui", "sans-serif"],
        // Comfortaa — logo text
        comfortaa: ["Comfortaa", "cursive"],
      },
      borderRadius: {
        brand: "12px",
      },
    },
  },
  plugins: [],
};
export default config;
