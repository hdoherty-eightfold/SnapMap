/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class', // Enable class-based dark mode
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Roboto', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Arial', 'sans-serif'],
        display: ['Roboto', 'sans-serif'],
      },
      fontSize: {
        'display-1': ['clamp(2.5rem, 6vw, 4rem)', { lineHeight: '1.1', letterSpacing: '-0.02em', fontWeight: '800' }],
        'display-2': ['clamp(2rem, 5.5vw, 3.5rem)', { lineHeight: '1.15', letterSpacing: '-0.015em', fontWeight: '700' }],
        'h1': ['clamp(1.75rem, 4vw, 2.5rem)', { lineHeight: '1.2', letterSpacing: '-0.01em', fontWeight: '700' }],
        'h2': ['clamp(1.5rem, 3.5vw, 2.1rem)', { lineHeight: '1.25', letterSpacing: '-0.01em', fontWeight: '700' }],
        'h3': ['clamp(1.25rem, 2.5vw, 1.75rem)', { lineHeight: '1.3', fontWeight: '600' }],
        'h4': ['clamp(1.125rem, 2vw, 1.5rem)', { lineHeight: '1.35', fontWeight: '600' }],
        'body-lg': ['1.125rem', { lineHeight: '1.625', fontWeight: '400' }],
        'body-sm': ['0.875rem', { lineHeight: '1.5', fontWeight: '400' }],
        'caption': ['0.75rem', { lineHeight: '1.4', letterSpacing: '0.01em', fontWeight: '500' }],
      },
      colors: {
        // Eightfold Complete Brand Color System
        eightfold: {
          teal: {
            50: '#f0faf8',
            100: '#d4f4ed',
            200: '#a9e8db',
            300: '#88e2d2',  // PRIMARY BRAND COLOR
            400: '#5ed4c1',
            500: '#3bc4af',
            600: '#2a9d8a',
            700: '#227d6e',
            800: '#1d6259',
            900: '#19504a',
          },
          navy: {
            50: '#edeef4',
            100: '#d4d5e5',
            200: '#a8abca',
            300: '#7d81b0',
            400: '#515695',
            500: '#262c7b',
            600: '#191841',  // PRIMARY TEXT COLOR
            700: '#131334',
            800: '#0e0f27',
            900: '#08091a',
          },
          electric: {
            50: '#e6e6ff',
            100: '#cccdff',
            200: '#999aff',
            300: '#6668ff',
            400: '#3335ff',
            500: '#0708ee',  // INTERACTIVE ELEMENTS
            600: '#0606be',
            700: '#04048e',
            800: '#03035f',
            900: '#01012f',
          },
          purple: {
            50: '#f3f0fc',
            100: '#e6e0f8',
            200: '#cdc1f1',
            300: '#b4a2ea',
            400: '#9b83e3',
            500: '#5741dc',  // GRADIENT COMPONENT
            600: '#4634b0',
            700: '#342784',
            800: '#231a58',
            900: '#110d2c',
          },
          purpleLight: {
            500: '#ae4fec',  // GRADIENT HIGHLIGHT
          },
          orange: {
            500: '#eb5854',  // ERROR/URGENT
          },
          bondi: {
            500: '#008FBF',  // ACCENT BLUE (from Brandfetch)
          },
          nile: {
            500: '#173A47',  // DARK BACKGROUNDS
          },
          plum: {
            500: '#7E3A77',  // BRAND HIGHLIGHT
          },
        },
        // Aliased colors for easier use
        primary: {
          50: '#f0faf8',
          100: '#d4f4ed',
          200: '#a9e8db',
          300: '#88e2d2',  // Eightfold teal
          400: '#5ed4c1',
          500: '#3bc4af',
          600: '#2a9d8a',
          700: '#227d6e',
          800: '#1d6259',
          900: '#191841',  // Eightfold navy
        },
        accent: {
          50: '#e6e6ff',
          100: '#cccdff',
          200: '#999aff',
          300: '#6668ff',
          400: '#3335ff',
          500: '#0708ee',  // Eightfold electric blue
          600: '#0606be',
          700: '#04048e',
          800: '#03035f',
          900: '#01012f',
        },
        success: {
          50: '#f0faf8',
          100: '#d4f4ed',
          200: '#a9e8db',
          300: '#88e2d2',
          400: '#5ed4c1',
          500: '#3bc4af',
          600: '#2a9d8a',
          700: '#227d6e',
          800: '#1d6259',
          900: '#19504a',
        },
        warning: {
          50: '#FFFBEB',
          100: '#FEF3C7',
          200: '#FDE68A',
          300: '#FCD34D',
          400: '#FBBF24',
          500: '#F59E0B',
          600: '#D97706',
          700: '#B45309',
          800: '#92400E',
          900: '#78350F',
        },
        error: {
          50: '#FEF2F2',
          100: '#FEE2E2',
          200: '#FECACA',
          300: '#FCA5A5',
          400: '#F87171',
          500: '#eb5854',  // Eightfold orange/red
          600: '#DC2626',
          700: '#B91C1C',
          800: '#991B1B',
          900: '#7F1D1D',
        },
      },
      borderRadius: {
        'pill': '112px',  // Eightfold signature pill shape
        'eightfold': '12px',  // Eightfold standard card radius
      },
      boxShadow: {
        'eightfold': '0 0 15px rgba(34, 31, 32, 0.1)',
        'eightfold-hover': '0 4px 20px rgba(34, 31, 32, 0.15)',
        'eightfold-teal': '0 2px 8px rgba(136, 226, 210, 0.25)',
        'eightfold-teal-hover': '0 4px 12px rgba(136, 226, 210, 0.35)',
        'eightfold-purple': '0 4px 16px rgba(87, 65, 220, 0.3)',
        'eightfold-purple-hover': '0 6px 20px rgba(87, 65, 220, 0.4)',
        'dark-eightfold': '0 4px 20px rgba(0, 0, 0, 0.4)',
      },
      backgroundImage: {
        'gradient-eightfold': 'linear-gradient(135deg, #88e2d2, #5741dc, #ae4fec, #eb5854)',
        'gradient-eightfold-cta': 'linear-gradient(135deg, #5741dc 0%, #ae4fec 50%, #eb5854 100%)',
        'gradient-eightfold-teal': 'linear-gradient(135deg, #88e2d2, #5ed4c1)',
        'gradient-eightfold-purple': 'linear-gradient(135deg, #5741dc, #ae4fec)',
        'gradient-navy': 'linear-gradient(180deg, #191841 0%, #173A47 100%)',
      },
      animation: {
        'spin': 'spin 1s linear infinite',
        'pulse': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce': 'bounce 1s infinite',
        'gradient': 'gradient 15s ease infinite',
        'slide-in': 'slideIn 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        'fade-in': 'fadeIn 0.3s ease-in-out',
      },
      keyframes: {
        gradient: {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
        slideIn: {
          '0%': { transform: 'translateX(-100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
      spacing: {
        '0.8': '0.2rem',
        '1.6': '0.4rem',
        '2.4': '0.6rem',
        '3.2': '0.8rem',    // Eightfold base unit
        '4.8': '1.2rem',
        '6.4': '1.6rem',    // Common padding
        '9.6': '2.4rem',    // Section padding
        '12.8': '3.2rem',
        '19.2': '4.8rem',
        '25.6': '6.4rem',
      },
      container: {
        center: true,
        padding: {
          DEFAULT: '1rem',
          sm: '1.5rem',
          lg: '2rem',
          xl: '2.5rem',
          '2xl': '3rem',
        },
        screens: {
          sm: '640px',
          md: '768px',
          lg: '1024px',
          xl: '1140px',   // Eightfold standard max-width
          '2xl': '1140px',
        },
      },
    },
  },
  plugins: [],
}
