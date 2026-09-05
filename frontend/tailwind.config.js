/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        base: {
          950: "#12151A",
          900: "#181C22",
          800: "#20252C",
          700: "#2A3038",
          600: "#3A4149",
          500: "#5A6270",
          400: "#838B99",
          300: "#AAB2BE",
          100: "#E7EAEE",
        },
        signal: {
          teal: "#2DD9C4",
          amber: "#F0A93B",
          red: "#EF5A5A",
          blue: "#4C8DFF",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
};
