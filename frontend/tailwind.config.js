/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: {
                    50: '#eff6ff',
                    100: '#dbeafe',
                    200: '#bfdbfe',
                    300: '#93c5fd',
                    400: '#60a5fa',
                    500: '#3b82f6',
                    600: '#2563eb',
                    700: '#1d4ed8',
                    800: '#1e40af',
                    900: '#1e3a8a',
                },
                dark: {
                    900: '#000000',
                    800: '#0a0a0a',
                    700: '#1a1a1a',
                    600: '#2a2a2a',
                    500: '#3a3a3a',
                }
            },
            fontFamily: {
                sans: ['-apple-system', 'BlinkMacSystemFont', 'SF Pro Display', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'sans-serif'],
            },
            animation: {
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'glow': 'glow 2s ease-in-out infinite',
            },
            keyframes: {
                glow: {
                    '0%, 100%': { opacity: 1 },
                    '50%': { opacity: 0.5 },
                }
            }
        },
    },
    plugins: [],
    darkMode: 'class',
}
