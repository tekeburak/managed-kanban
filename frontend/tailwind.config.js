/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          "ui-sans-serif",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "sans-serif",
        ],
        mono: ["ui-monospace", "SF Mono", "Menlo", "monospace"],
      },
      colors: {
        ink: {
          900: "#0f1115",
          700: "#3a3f47",
          500: "#6b7280",
          300: "#d1d5db",
        },
        canvas: "#f6f4ee",
      },
    },
  },
  plugins: [],
};
