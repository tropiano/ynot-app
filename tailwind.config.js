module.exports = {
  content: [
    "./templates/**/*.{html,js}",
    "./node_modules/flowbite/**/*.js",
    "./static/**/*.{js,css}",
  ],
  theme: {
    extend: {
      fontFamily: {
      'montserrat': ['"Montserrat One"', 'sans-serif'],
      'kanit': ['Kanit', 'sans-serif'],
      'indieflower': ['Indie Flower', 'sans-serif'],
      'madimi': ['"Madimi One"', 'sans-serif'],
    }},
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('flowbite/plugin'),
    // require('daisyui/base'),
  ],
  daisyui: {
    themes: ["light", "dark"],
  }
}