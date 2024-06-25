/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: 'media',
  content: ["./templates/**/*.html",
            "./node_modules/flowbit/**/*.js",
            "./templates/**/**/*.html",
            "./apps/**/templates/*.html",
            "./apps/resume_builder/templates/**/*.html",
            "./apps/resume_builder/templates/components/*.html"
  ],
  theme: {
    extend: {},
  },
  plugins: [
      require("flowbite/plugin")
  ],
}

