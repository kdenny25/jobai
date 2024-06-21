/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: 'media',
  content: ["./templates/**/*.html",
            "./node_modules/flowbit/**/*.js",
            "./templates/**/**/*.html",
            "./apps/**/templates/*.html"
  ],
  theme: {
    extend: {},
  },
  plugins: [
      require("flowbite/plugin")
  ],
}

