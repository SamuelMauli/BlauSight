/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      // ✅ AQUI ESTÁ A CORREÇÃO PRINCIPAL
      // Definimos nossa paleta de cores para que o Tailwind
      // possa gerar as classes como 'bg-bg-primary-light'.
      colors: {
        'bg-primary-light': '#f7f9fc',
        'bg-secondary-light': '#ffffff',
        'bg-primary-dark': '#0d1117',
        'bg-secondary-dark': '#161b22',

        'text-primary-light': '#1f2937',
        'text-secondary-light': '#6b7280',
        'text-primary-dark': '#e6edf3',
        'text-secondary-dark': '#8b949e',

        'accent-primary': '#3b82f6',
        'accent-primary-hover': '#2563eb',
        'accent-secondary': '#dbeafe',
        'accent-secondary-dark': '#1e40af',

        'border-light': '#e5e7eb',
        'border-dark': '#30363d',

        'success': '#10b981',
        'danger': '#ef4444',
        'warning': '#f59e0b',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fade-in 0.5s ease-out forwards',
      },
      keyframes: {
        'fade-in': {
          'from': { opacity: '0', transform: 'translateY(10px)' },
          'to': { opacity: '1', transform: 'translateY(0)' },
        }
      },
    },
  },
  plugins: [],
}