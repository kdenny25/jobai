/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: 'media',
  content: ["./templates/**/*.html",
            "./node_modules/flowbit/**/*.js"
  ],
  theme: {
    extend: {},
  },
  plugins: [
      require("flowbite/plugin")
  ],
}

