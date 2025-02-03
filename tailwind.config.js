/** @type {import('tailwindcss').Config} */
const plugin = require('tailwindcss/plugin');

module.exports = {
  content: ["./app/templates/**/*.html"],
  theme: {
    extend: {
      gridTemplateColumns: {
        fluid: "repeat(auto-fit, minmax(400px, 1fr))",
      },
      colors: {
        primary: {
          50: "#f6e5d3",
          100: "#f6e5d3",
          200: "#f0d3b8",
          300: "#e6b48b",
          400: "#db8e5c",
          500: "#d2713d",
          600: "#c45c32",
          700: "#a3472b",
          800: "#833b29",
          900: "#6a3224",
          950: "#391811",
        },
      },
      fontFamily: {
        primary: ['"Noto Kufi Arabic"', 'serif'],
        secondary: ['sans-serif'],
      },
    },
  },
  plugins: [],
};
