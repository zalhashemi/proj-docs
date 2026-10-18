/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: '#14b8a6',
          600: '#0d9488',
          700: '#0f766e',
        },
        secondary: '#f97316',
        accent: '#8b5cf6',
        ink: '#1e293b',
        danger: '#e11d48',
      },
      fontFamily: {
        sans: ['Poppins', 'ui-sans-serif', 'system-ui'],
        display: ['"Playfair Display"', 'serif'],
      },
    },
  },
  plugins: [],
}
