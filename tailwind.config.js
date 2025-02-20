/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/templates/**/*.html", "./app/static/js/*.js"],
  theme: {
    extend: {
      gridTemplateColumns: {
        fluid: "repeat(auto-fit, minmax(350px, 1fr))",
      },
      backgroundSize: {
        900: "900px", // Add your custom size here
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
        primary: ['"Noto Kufi Arabic"', "serif"],
        secondary: ["sans-serif"],
      },
      animation: {
        "spin-slow": "spin 1.5s linear infinite",
      },
    },
  },
  plugins: [],
};
