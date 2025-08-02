module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#4CAF50",
        accent: "#FFC107",
        danger: "#f44336",
        // brand colors as per your design
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui"],
      }
    },
  },
  plugins: [],
}
