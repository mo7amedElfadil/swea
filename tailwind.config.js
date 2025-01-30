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
          50: "#f2f9fd",
          100: "#e3f0fb",
          200: "#c2e2f5",
          300: "#8ccbed",
          400: "#4eafe2",
          500: "#2691c9",
          600: "#1978b0",
          700: "#15608F",
          800: "#165276",
          900: "#174463",
          950: "#102b41",
        },
        secondary: "#FF9D01",
      },
      //fontFamily: {
      //  primary: ["Geist", "sans-serif"],
      //  secondary: ["sans-serif"],
      //},
    },
  },
  plugins: [],
};
