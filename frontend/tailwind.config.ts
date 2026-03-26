import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          purple:          "#904cd8",
          blue:            "#2656dd",
          pink:            "#ea7db7",
          "purple-light":  "#a170e0",
          "purple-lighter":"#b892e8",
          "blue-light":    "#4c6ee5",
          "blue-lighter":  "#6e8ee5",
          "pink-light":    "#edb4d2",
          "pink-lightest": "#f6d5e5",
        },
      },
      fontFamily: {
        heading: ["Brielle", "Georgia", "serif"],
        body:    ["Montserrat", "sans-serif"],
        logo:    ["Comfortaa", "cursive"],
      },
    },
  },
  plugins: [],
};
export default config;
