export default  {
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
      // add Josefin Sans and Arial
      'josefin': ['"Josefin Sans"', 'Arial', 'sans-serif'],
    },
      colors: {
      'yn-blue': '#01438f',
      'yn-gray': '#eeeeee',
      'yn-red': '#b21f85',
      'yn-pink': '#e8aeb8',
      'yn-maintext': '#000000',
      'yn-background': '#881264',
      'yn-sectext': '#331628',
      'yn-white': '#fff8f5',   
        },
    },
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