# SnapMap Tailwind Implementation Examples
## Ready-to-Use Component Code with Eightfold.ai Design System

**Document Version:** 1.0
**Last Updated:** November 7, 2025
**Companion to:** EIGHTFOLD_UI_REBRANDING_GUIDE.md, SNAPMAP_SCREEN_DESIGNS.md

---

## Table of Contents

1. [Updated Tailwind Configuration](#updated-tailwind-configuration)
2. [Button Components](#button-components)
3. [Card Components](#card-components)
4. [Form Components](#form-components)
5. [Navigation Components](#navigation-components)
6. [Upload Zone Component](#upload-zone-component)
7. [Field Mapping Components](#field-mapping-components)
8. [Progress & Loading Components](#progress--loading-components)
9. [Utility Classes](#utility-classes)
10. [Animation Examples](#animation-examples)

---

## Updated Tailwind Configuration

### Complete `tailwind.config.js`

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Eightfold Official Brand Colors
        eightfold: {
          teal: '#88e2d2',
          navy: '#191841',
          'electric-blue': '#0708ee',
          'quantum-indigo': '#5741dc',
          'smart-orange': '#eb5854',
          'deep-magenta': '#a1378b',
          'purple-light': '#ae4fec',
          'fusion-gold': '#f8a456',
        },
        // Primary palette based on teal
        primary: {
          50: '#f0fdfb',
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
        // Accent palette based on electric blue
        accent: {
          50: '#ebebff',
          100: '#d4d4ff',
          200: '#a9a9ff',
          300: '#5e5eff',
          400: '#2a2aff',
          500: '#0708ee',  // Electric blue
          600: '#0606c7',
          700: '#05059f',
          800: '#040477',
          900: '#030359',
        },
        // Semantic colors
        success: {
          50: '#ECFDF5',
          100: '#D1FAE5',
          200: '#A7F3D0',
          300: '#6EE7B7',
          400: '#34D399',
          500: '#10B981',
          600: '#059669',
          700: '#047857',
          800: '#065F46',
          900: '#064E3B',
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
          500: '#EF4444',
          600: '#DC2626',
          700: '#B91C1C',
          800: '#991B1B',
          900: '#7F1D1D',
        },
      },
      fontFamily: {
        sans: [
          'Gilroy',
          'Montserrat',
          'Inter',
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'Roboto',
          'Helvetica Neue',
          'Arial',
          'sans-serif',
        ],
        mono: ['Monaco', 'Menlo', 'Courier New', 'monospace'],
      },
      fontSize: {
        'h1': 'clamp(2rem, 5.5vw, 3.5rem)',
        'h2': 'clamp(1.6rem, 3.8vw, 2.5rem)',
        'h3': 'clamp(1.4rem, 2.5vw, 2rem)',
        'h4': 'clamp(1.2rem, 2vw, 1.5rem)',
      },
      borderRadius: {
        'pill': '112px',
        'xl': '12px',
      },
      boxShadow: {
        'card': '0 0 15px rgba(34, 31, 32, 0.1)',
        'card-hover': '0 4px 24px rgba(34, 31, 32, 0.12)',
        'button': '0 2px 8px rgba(136, 226, 210, 0.2)',
        'button-hover': '0 4px 12px rgba(136, 226, 210, 0.3)',
        'glow-teal': '0 0 24px rgba(136, 226, 210, 0.4)',
        'glow-purple': '0 0 24px rgba(87, 65, 220, 0.4)',
      },
      transitionTimingFunction: {
        'eightfold': 'cubic-bezier(0.87, 0, 0.13, 1)',
      },
      animation: {
        'gradient-shift': 'gradientShift 15s ease infinite',
        'fade-in': 'fadeIn 0.5s cubic-bezier(0.87, 0, 0.13, 1) forwards',
        'slide-in-right': 'slideInRight 0.3s cubic-bezier(0.87, 0, 0.13, 1) forwards',
        'slide-in-up': 'slideInUp 0.5s cubic-bezier(0.87, 0, 0.13, 1) forwards',
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
        'shimmer': 'shimmer 2s linear infinite',
      },
      keyframes: {
        gradientShift: {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideInRight: {
          '0%': { transform: 'translateX(100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        slideInUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 12px rgba(136, 226, 210, 0.3)' },
          '50%': { boxShadow: '0 0 24px rgba(136, 226, 210, 0.6)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '200% 0' },
          '100%': { backgroundPosition: '-200% 0' },
        },
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(135deg, #88e2d2 0%, #5741dc 50%, #0708ee 100%)',
        'gradient-hero': 'linear-gradient(135deg, #191841 0%, #5741dc 100%)',
        'gradient-warm': 'linear-gradient(135deg, #eb5854 0%, #f8a456 100%)',
        'gradient-cool': 'linear-gradient(135deg, #0708ee 0%, #88e2d2 100%)',
      },
    },
  },
  plugins: [],
}
```

---

## Button Components

### Primary Teal Button (Main CTA)

```tsx
// Component usage
<button className="
  px-10 py-3
  bg-eightfold-teal
  text-eightfold-navy
  font-semibold text-base
  rounded-pill
  shadow-button
  hover:bg-primary-400
  hover:shadow-button-hover
  hover:-translate-y-0.5
  active:translate-y-0
  focus:outline-none focus:ring-3 focus:ring-eightfold-teal/40
  disabled:opacity-60 disabled:cursor-not-allowed disabled:transform-none
  transition-all duration-300 ease-eightfold
  inline-flex items-center justify-center gap-2
">
  Get Started
</button>
```

### Secondary Outline Button

```tsx
<button className="
  px-10 py-3
  bg-transparent
  border-2 border-eightfold-teal
  text-eightfold-teal
  font-semibold text-base
  rounded-pill
  hover:bg-eightfold-teal
  hover:text-eightfold-navy
  hover:shadow-button-hover
  hover:-translate-y-0.5
  active:translate-y-0
  focus:outline-none focus:ring-3 focus:ring-eightfold-teal/40
  transition-all duration-300 ease-eightfold
  inline-flex items-center justify-center gap-2
">
  Learn More
</button>
```

### Gradient CTA Button (Hero Actions)

```tsx
<button className="
  px-14 py-4
  bg-gradient-primary
  text-white
  font-bold text-lg
  rounded-pill
  shadow-glow-purple
  hover:shadow-glow-teal
  hover:-translate-y-0.5
  active:translate-y-0
  focus:outline-none focus:ring-3 focus:ring-eightfold-quantum-indigo/40
  transition-all duration-300 ease-eightfold
  inline-flex items-center justify-center gap-2
  animate-pulse-glow
">
  Start Mapping
</button>
```

### Ghost Button (Subtle Actions)

```tsx
<button className="
  px-4 py-2
  bg-transparent
  text-gray-700 dark:text-gray-300
  font-medium text-sm
  rounded-lg
  hover:bg-eightfold-teal/10
  hover:text-eightfold-teal
  focus:outline-none focus:ring-2 focus:ring-eightfold-teal/40
  transition-all duration-200
  inline-flex items-center justify-center gap-2
">
  Cancel
</button>
```

### Icon Button (Small Actions)

```tsx
<button className="
  w-10 h-10
  flex items-center justify-center
  bg-transparent
  text-gray-600 dark:text-gray-400
  rounded-lg
  hover:bg-eightfold-teal/10
  hover:text-eightfold-teal
  focus:outline-none focus:ring-2 focus:ring-eightfold-teal/40
  transition-all duration-200
">
  <svg className="w-5 h-5" />
</button>
```

### Button with Loading State

```tsx
<button
  disabled={isLoading}
  className="
    px-10 py-3
    bg-eightfold-teal
    text-eightfold-navy
    font-semibold text-base
    rounded-pill
    shadow-button
    hover:bg-primary-400
    disabled:opacity-60 disabled:cursor-not-allowed
    transition-all duration-300 ease-eightfold
    inline-flex items-center justify-center gap-2
  "
>
  {isLoading ? (
    <>
      <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
      </svg>
      Processing...
    </>
  ) : (
    'Upload File'
  )}
</button>
```

---

## Card Components

### Standard Card

```tsx
<div className="
  bg-white dark:bg-gray-800/50
  border border-gray-200 dark:border-gray-700
  rounded-xl
  p-8
  shadow-card
  transition-all duration-300 ease-eightfold
">
  {/* Card content */}
</div>
```

### Hoverable Card (Interactive)

```tsx
<div className="
  bg-white dark:bg-gray-800/50
  border border-gray-200 dark:border-gray-700
  rounded-xl
  p-8
  shadow-card
  hover:shadow-card-hover
  hover:-translate-y-1
  cursor-pointer
  transition-all duration-300 ease-eightfold
">
  {/* Card content */}
</div>
```

### Gradient Hero Card

```tsx
<div className="
  bg-gradient-hero
  rounded-xl
  p-12
  text-white
  relative
  overflow-hidden
">
  {/* Decorative glow */}
  <div className="
    absolute top-0 right-0
    w-64 h-64
    bg-gradient-radial from-eightfold-teal/20 to-transparent
    rounded-full
    blur-3xl
  " />

  {/* Content */}
  <div className="relative z-10">
    <h1 className="text-h2 font-bold mb-4">Upload Your Data</h1>
    <p className="text-lg opacity-90">
      Transform HR data from any system to Eightfold format
    </p>
  </div>
</div>
```

### Feature Card with Accent Border

```tsx
<div className="
  bg-white dark:bg-gray-800/50
  border-2 border-eightfold-teal
  rounded-xl
  p-6
  shadow-card
  relative
  overflow-hidden
">
  {/* Accent corner */}
  <div className="
    absolute top-0 right-0
    w-24 h-24
    bg-gradient-to-br from-eightfold-teal/10 to-transparent
  " />

  {/* Content */}
  <div className="relative">
    <div className="text-3xl mb-3">✨</div>
    <h3 className="text-xl font-bold text-eightfold-navy dark:text-white mb-2">
      AI Powered
    </h3>
    <p className="text-gray-600 dark:text-gray-300">
      Semantic field mapping with 90% accuracy
    </p>
  </div>
</div>
```

### Blur Backdrop Card (Glass Effect)

```tsx
<div className="
  bg-white/80 dark:bg-gray-900/80
  backdrop-blur-xl
  border border-white/30 dark:border-gray-700/30
  rounded-xl
  p-6
  shadow-card
">
  {/* Card content */}
</div>
```

---

## Form Components

### Text Input

```tsx
<div className="space-y-2">
  <label className="
    block
    text-sm font-semibold
    text-gray-900 dark:text-white
    mb-2
  ">
    Email Address
  </label>
  <input
    type="email"
    placeholder="you@company.com"
    className="
      w-full
      px-4 py-3
      bg-white dark:bg-gray-900
      border-2 border-gray-300 dark:border-gray-600
      rounded-lg
      text-gray-900 dark:text-white
      placeholder:text-gray-400
      focus:outline-none
      focus:border-eightfold-teal
      focus:ring-3 focus:ring-eightfold-teal/20
      disabled:bg-gray-100 disabled:cursor-not-allowed
      transition-all duration-200
    "
  />
</div>
```

### Select Dropdown

```tsx
<div className="space-y-2">
  <label className="
    block
    text-sm font-semibold
    text-gray-900 dark:text-white
    mb-2
  ">
    Entity Type
  </label>
  <select className="
    w-full
    px-4 py-3
    bg-white dark:bg-gray-900
    border-2 border-gray-300 dark:border-gray-600
    rounded-lg
    text-gray-900 dark:text-white
    font-medium
    cursor-pointer
    focus:outline-none
    focus:border-eightfold-teal
    focus:ring-3 focus:ring-eightfold-teal/20
    transition-all duration-200
    appearance-none
    bg-[url('data:image/svg+xml,...')]
    bg-no-repeat
    bg-[right_12px_center]
    bg-[length:20px]
    pr-10
  ">
    <option value="employee">Employee</option>
    <option value="candidate">Candidate</option>
    <option value="position">Position</option>
  </select>
</div>
```

### Checkbox

```tsx
<label className="
  flex items-center gap-3
  cursor-pointer
  group
">
  <input
    type="checkbox"
    className="
      w-5 h-5
      rounded
      border-2 border-gray-300
      text-eightfold-teal
      focus:ring-3 focus:ring-eightfold-teal/20
      transition-all duration-200
      cursor-pointer
    "
  />
  <span className="
    text-sm text-gray-700 dark:text-gray-300
    group-hover:text-eightfold-teal
    transition-colors duration-200
  ">
    Remember my preferences
  </span>
</label>
```

### Radio Button (Custom Style)

```tsx
<div className="flex gap-4">
  <label className="
    flex items-center gap-3
    cursor-pointer
    group
  ">
    <div className="relative">
      <input
        type="radio"
        name="theme"
        className="
          sr-only
          peer
        "
      />
      <div className="
        w-5 h-5
        border-2 border-gray-300
        rounded-full
        peer-checked:border-eightfold-teal
        peer-focus:ring-3 peer-focus:ring-eightfold-teal/20
        transition-all duration-200
      " />
      <div className="
        absolute top-1/2 left-1/2
        -translate-x-1/2 -translate-y-1/2
        w-2.5 h-2.5
        bg-eightfold-teal
        rounded-full
        opacity-0
        peer-checked:opacity-100
        transition-opacity duration-200
      " />
    </div>
    <span className="
      text-sm text-gray-700 dark:text-gray-300
      group-hover:text-eightfold-teal
      transition-colors duration-200
    ">
      Light Mode
    </span>
  </label>
</div>
```

---

## Navigation Components

### Sidebar Nav Item (Active State)

```tsx
<button className="
  w-full
  flex items-center gap-3
  px-4 py-3
  rounded-lg
  text-sm font-medium
  text-gray-700 dark:text-gray-300
  hover:bg-eightfold-teal/10
  hover:text-eightfold-teal
  data-[active=true]:bg-gradient-to-r
  data-[active=true]:from-eightfold-teal/15
  data-[active=true]:to-eightfold-quantum-indigo/10
  data-[active=true]:text-eightfold-teal
  data-[active=true]:font-semibold
  data-[active=true]:border-l-4
  data-[active=true]:border-eightfold-teal
  transition-all duration-200
  relative
">
  <span className="text-xl">📁</span>
  <span>Upload</span>

  {/* Badge */}
  <span className="
    ml-auto
    px-2 py-0.5
    bg-success-100 dark:bg-success-900/30
    text-success-700 dark:text-success-400
    text-xs font-semibold
    rounded-full
  ">
    Done
  </span>
</button>
```

### Breadcrumb

```tsx
<nav className="flex items-center gap-2 text-sm">
  <a href="/" className="
    text-gray-500 dark:text-gray-400
    hover:text-eightfold-teal
    transition-colors duration-200
  ">
    Home
  </a>
  <span className="text-gray-400">/</span>
  <span className="
    text-gray-900 dark:text-white
    font-semibold
  ">
    Upload
  </span>
</nav>
```

### Tab Navigation

```tsx
<div className="
  flex items-center gap-1
  p-1
  bg-gray-100 dark:bg-gray-800
  rounded-lg
">
  <button className="
    px-4 py-2
    text-sm font-medium
    rounded-md
    text-gray-700 dark:text-gray-300
    hover:text-gray-900 dark:hover:text-white
    data-[active=true]:bg-white
    data-[active=true]:dark:bg-gray-700
    data-[active=true]:text-eightfold-teal
    data-[active=true]:shadow-sm
    transition-all duration-200
  ">
    API
  </button>
  <button className="
    px-4 py-2
    text-sm font-medium
    rounded-md
    text-gray-700 dark:text-gray-300
    hover:text-gray-900 dark:hover:text-white
    transition-all duration-200
  ">
    Display
  </button>
  <button className="
    px-4 py-2
    text-sm font-medium
    rounded-md
    text-gray-700 dark:text-gray-300
    hover:text-gray-900 dark:hover:text-white
    transition-all duration-200
  ">
    About
  </button>
</div>
```

---

## Upload Zone Component

### Drag & Drop Zone with States

```tsx
<div className={`
  relative
  border-2 border-dashed
  rounded-xl
  p-16
  text-center
  transition-all duration-300 ease-eightfold
  ${isDragging
    ? 'border-eightfold-teal bg-eightfold-teal/10 scale-[1.02] shadow-glow-teal'
    : 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900'
  }
  ${isSuccess
    ? 'border-success-500 bg-success-50 dark:bg-success-900/20'
    : ''
  }
  ${isError
    ? 'border-error-500 bg-error-50 dark:bg-error-900/20'
    : ''
  }
  hover:border-eightfold-teal
  hover:bg-eightfold-teal/5
`}>
  {/* Upload Icon Circle */}
  <div className="
    w-20 h-20
    mx-auto mb-6
    flex items-center justify-center
    bg-eightfold-teal/10
    rounded-full
  ">
    <svg className="w-10 h-10 text-eightfold-teal" />
  </div>

  {/* Text */}
  <p className="
    text-lg font-semibold
    text-gray-900 dark:text-white
    mb-2
  ">
    Drop your file here, or{' '}
    <span className="text-eightfold-teal">browse</span>
  </p>
  <p className="
    text-sm text-gray-500 dark:text-gray-400
  ">
    Supports CSV and Excel (.csv, .xlsx)
  </p>

  {/* Browse Button */}
  <button className="
    mt-6
    px-10 py-3
    bg-eightfold-teal
    text-eightfold-navy
    font-semibold
    rounded-pill
    shadow-button
    hover:shadow-button-hover
    hover:-translate-y-0.5
    transition-all duration-300 ease-eightfold
    inline-flex items-center justify-center gap-2
  ">
    <svg className="w-5 h-5" />
    Browse Files
  </button>
</div>
```

---

## Field Mapping Components

### Source Field Card (Mapped with High Confidence)

```tsx
<div className="
  flex items-center gap-3
  p-4
  bg-eightfold-teal/10
  border-2 border-eightfold-teal
  rounded-lg
  cursor-pointer
  transition-all duration-200
  hover:shadow-md
  hover:translate-x-1
">
  {/* Checkbox */}
  <input type="checkbox" className="
    w-4 h-4
    rounded
    text-eightfold-teal
    border-eightfold-teal
  " />

  {/* Icon */}
  <div className="
    w-8 h-8
    flex items-center justify-center
    bg-white dark:bg-gray-800
    rounded-md
    text-lg
  ">
    📝
  </div>

  {/* Field Info */}
  <div className="flex-1">
    <div className="flex items-center gap-2">
      <span className="
        text-sm font-semibold
        text-gray-900 dark:text-white
        font-mono
      ">
        firstName
      </span>

      {/* Confidence Badge */}
      <span className="
        px-2 py-0.5
        bg-eightfold-teal/20
        border border-eightfold-teal
        text-eightfold-teal
        text-xs font-bold
        rounded-full
      ">
        95%
      </span>

      {/* AI Badge */}
      <span className="
        px-2 py-0.5
        bg-gradient-primary
        text-white
        text-[10px] font-bold
        uppercase tracking-wider
        rounded-full
      ">
        AI
      </span>
    </div>
    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
      5 samples matched
    </p>
  </div>

  {/* Checkmark */}
  <div className="
    w-6 h-6
    flex items-center justify-center
    bg-eightfold-teal
    text-white
    rounded-full
    text-sm
  ">
    ✓
  </div>
</div>
```

### Target Field Card (Required)

```tsx
<div className="
  relative
  p-4
  bg-white dark:bg-gray-800/50
  border-2 border-gray-200 dark:border-gray-700
  rounded-lg
  data-[mapped=true]:border-eightfold-teal
  data-[mapped=true]:bg-eightfold-teal/5
  transition-all duration-200
">
  {/* Required indicator */}
  <span className="
    absolute -left-3 top-3
    text-error-500 text-xl
  ">
    *
  </span>

  {/* Field Info */}
  <div className="flex items-start justify-between">
    <div>
      <span className="
        text-sm font-semibold
        text-gray-900 dark:text-white
        font-mono
      ">
        firstName
      </span>
      <p className="
        text-xs text-gray-500 dark:text-gray-400
        mt-1
      ">
        Employee's first name
      </p>
      <div className="flex gap-2 mt-2">
        <span className="
          px-2 py-0.5
          bg-error-100 dark:bg-error-900/30
          text-error-700 dark:text-error-400
          text-[10px] font-semibold
          uppercase tracking-wider
          rounded-full
        ">
          Required
        </span>
        <span className="
          px-2 py-0.5
          bg-gray-100 dark:bg-gray-800
          text-gray-600 dark:text-gray-400
          text-[10px] font-semibold
          uppercase tracking-wider
          rounded-full
        ">
          String
        </span>
      </div>
    </div>
  </div>
</div>
```

### Connection Line (SVG)

```tsx
<svg className="absolute inset-0 pointer-events-none">
  <defs>
    <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stopColor="#88e2d2" />
      <stop offset="100%" stopColor="#5741dc" />
    </linearGradient>
  </defs>
  <line
    x1={sourceX}
    y1={sourceY}
    x2={targetX}
    y2={targetY}
    stroke="url(#lineGradient)"
    strokeWidth="3"
    strokeLinecap="round"
    className="
      drop-shadow-[0_0_4px_rgba(136,226,210,0.4)]
      animate-pulse-glow
    "
  />
</svg>
```

---

## Progress & Loading Components

### Linear Progress Bar

```tsx
<div className="w-full">
  <div className="
    flex items-center justify-between
    mb-2
  ">
    <span className="text-sm font-semibold text-gray-900 dark:text-white">
      Uploading employee.xml
    </span>
    <span className="text-sm font-semibold text-eightfold-teal">
      75%
    </span>
  </div>

  <div className="
    w-full h-3
    bg-gray-200 dark:bg-gray-700
    rounded-full
    overflow-hidden
  ">
    <div
      className="
        h-full
        bg-gradient-to-r from-eightfold-teal to-eightfold-quantum-indigo
        rounded-full
        transition-all duration-500 ease-out
        shadow-glow-teal
        animate-shimmer
        bg-[length:200%_100%]
      "
      style={{ width: '75%' }}
    />
  </div>

  <p className="
    text-xs text-gray-500 dark:text-gray-400
    mt-1
  ">
    1.8 MB of 2.4 MB • 45 seconds remaining
  </p>
</div>
```

### Circular Loading Spinner

```tsx
<div className="
  inline-block
  w-12 h-12
  border-4 border-eightfold-teal/20
  border-t-eightfold-teal
  rounded-full
  animate-spin
" />
```

### Loading Skeleton

```tsx
<div className="space-y-4 animate-pulse">
  {/* Header skeleton */}
  <div className="
    h-8 w-1/3
    bg-gray-200 dark:bg-gray-700
    rounded
  " />

  {/* Content skeleton */}
  <div className="space-y-2">
    <div className="
      h-4 w-full
      bg-gray-200 dark:bg-gray-700
      rounded
    " />
    <div className="
      h-4 w-5/6
      bg-gray-200 dark:bg-gray-700
      rounded
    " />
    <div className="
      h-4 w-4/6
      bg-gray-200 dark:bg-gray-700
      rounded
    " />
  </div>
</div>
```

### Pulsing Dot Indicator

```tsx
<div className="flex items-center gap-2">
  <div className="
    w-2 h-2
    bg-eightfold-teal
    rounded-full
    animate-pulse
  " />
  <span className="text-sm text-gray-600 dark:text-gray-400">
    Processing...
  </span>
</div>
```

---

## Utility Classes

### Common Text Styles

```tsx
// Page Header
<h1 className="
  text-h1
  font-bold
  text-eightfold-navy dark:text-white
  leading-tight
  tracking-tight
">

// Section Header
<h2 className="
  text-h2
  font-bold
  text-eightfold-navy dark:text-white
  leading-tight
">

// Card Title
<h3 className="
  text-xl
  font-semibold
  text-eightfold-navy dark:text-white
">

// Body Text
<p className="
  text-base
  text-gray-700 dark:text-gray-300
  leading-relaxed
">

// Caption/Helper Text
<p className="
  text-sm
  text-gray-500 dark:text-gray-400
">

// Label (Uppercase)
<label className="
  text-xs
  font-semibold
  text-gray-700 dark:text-gray-300
  uppercase
  tracking-wider
">
```

### Badge Styles

```tsx
// Success Badge
<span className="
  inline-flex items-center
  px-3 py-1
  bg-success-100 dark:bg-success-900/30
  text-success-700 dark:text-success-400
  text-xs font-semibold
  uppercase tracking-wider
  rounded-full
">
  Success
</span>

// Warning Badge
<span className="
  inline-flex items-center
  px-3 py-1
  bg-warning-100 dark:bg-warning-900/30
  text-warning-700 dark:text-warning-400
  text-xs font-semibold
  uppercase tracking-wider
  rounded-full
">
  Warning
</span>

// Teal Badge (AI/Primary)
<span className="
  inline-flex items-center
  px-3 py-1
  bg-eightfold-teal/20
  border border-eightfold-teal
  text-eightfold-teal
  text-xs font-semibold
  uppercase tracking-wider
  rounded-full
">
  AI Powered
</span>

// Gradient Badge
<span className="
  inline-flex items-center
  px-3 py-1
  bg-gradient-primary
  text-white
  text-xs font-bold
  uppercase tracking-wider
  rounded-full
  shadow-sm
">
  Premium
</span>
```

### Container Utilities

```tsx
// Page Container
<div className="
  max-w-7xl
  mx-auto
  px-8
  py-8
">

// Narrow Container (Forms)
<div className="
  max-w-2xl
  mx-auto
  px-8
">

// Full Width Section
<section className="
  w-full
  py-16
  bg-gray-50 dark:bg-gray-900
">
```

---

## Animation Examples

### Fade In on Mount

```tsx
<div className="
  animate-fade-in
  opacity-0
">
  Content appears smoothly
</div>
```

### Slide In from Right (Toast/Notification)

```tsx
<div className="
  animate-slide-in-right
">
  Notification message
</div>
```

### Hover Lift Effect

```tsx
<div className="
  transition-all duration-300 ease-eightfold
  hover:-translate-y-1
  hover:shadow-card-hover
">
  Interactive card
</div>
```

### Gradient Animation (Background)

```tsx
<div className="
  bg-gradient-to-r
  from-eightfold-teal
  via-eightfold-quantum-indigo
  to-accent-500
  bg-[length:200%_100%]
  animate-gradient-shift
">
  Animated gradient background
</div>
```

### Pulse Glow Effect

```tsx
<button className="
  animate-pulse-glow
  shadow-glow-teal
">
  Primary Action
</button>
```

---

## Complete Page Example: Upload Screen

```tsx
export const FileUpload = () => {
  return (
    <div className="max-w-4xl mx-auto animate-fade-in">
      {/* Hero Card */}
      <div className="
        bg-gradient-hero
        rounded-xl
        p-12
        text-white
        relative
        overflow-hidden
        mb-6
      ">
        {/* Decorative glow */}
        <div className="
          absolute top-0 right-0
          w-64 h-64
          bg-gradient-radial from-eightfold-teal/20 to-transparent
          rounded-full
          blur-3xl
        " />

        {/* Content */}
        <div className="relative z-10">
          {/* Icon */}
          <div className="
            w-16 h-16
            mb-6
            flex items-center justify-center
            bg-white/10
            backdrop-blur-sm
            rounded-2xl
          ">
            <span className="text-3xl">✨</span>
          </div>

          {/* Title */}
          <h1 className="text-h2 font-bold mb-4">
            Upload Your Data
          </h1>
          <p className="text-lg opacity-90 mb-8">
            Transform HR data from any system to Eightfold format
          </p>

          {/* Entity Selector */}
          <div className="max-w-md">
            <label className="
              block
              text-sm font-semibold
              mb-2
              opacity-90
            ">
              📋 Select Entity Type
            </label>
            <select className="
              w-full
              px-4 py-3
              bg-white/10
              backdrop-blur-sm
              border-2 border-white/20
              rounded-lg
              text-white
              font-semibold
              cursor-pointer
              hover:border-eightfold-teal
              focus:outline-none
              focus:border-eightfold-teal
              focus:ring-3 focus:ring-eightfold-teal/30
              transition-all duration-200
            ">
              <option value="employee">Employee - Master data</option>
            </select>
          </div>
        </div>
      </div>

      {/* Upload Zone */}
      <div className="
        relative
        border-2 border-dashed border-gray-300
        rounded-xl
        p-16
        text-center
        bg-white dark:bg-gray-900
        hover:border-eightfold-teal
        hover:bg-eightfold-teal/5
        transition-all duration-300 ease-eightfold
      ">
        {/* Upload Icon */}
        <div className="
          w-20 h-20
          mx-auto mb-6
          flex items-center justify-center
          bg-eightfold-teal/10
          rounded-full
        ">
          <svg className="w-10 h-10 text-eightfold-teal" />
        </div>

        {/* Text */}
        <p className="
          text-lg font-semibold
          text-gray-900 dark:text-white
          mb-2
        ">
          Drop your file here, or{' '}
          <span className="text-eightfold-teal">browse</span>
        </p>
        <p className="
          text-sm text-gray-500 dark:text-gray-400
          mb-6
        ">
          Supports CSV and Excel (.csv, .xlsx)
        </p>

        {/* Button */}
        <button className="
          px-10 py-3
          bg-eightfold-teal
          text-eightfold-navy
          font-semibold
          rounded-pill
          shadow-button
          hover:shadow-button-hover
          hover:-translate-y-0.5
          transition-all duration-300 ease-eightfold
          inline-flex items-center justify-center gap-2
        ">
          <svg className="w-5 h-5" />
          Browse Files
        </button>
      </div>

      {/* Tip Card */}
      <div className="
        mt-6
        p-4
        bg-eightfold-teal/10
        border border-eightfold-teal/30
        rounded-xl
        flex items-start gap-3
      ">
        <span className="text-2xl">💡</span>
        <div>
          <h3 className="
            text-sm font-semibold
            text-eightfold-navy dark:text-white
            mb-1
          ">
            Getting Started
          </h3>
          <p className="text-sm text-gray-700 dark:text-gray-300">
            Upload CSV or Excel files up to 100MB. The system will automatically
            detect the entity type from your data.
          </p>
        </div>
      </div>
    </div>
  );
};
```

---

## Tips for Implementation

### 1. Use Composition

Create reusable base classes:
```tsx
// Base button classes
const baseButton = "px-10 py-3 font-semibold rounded-pill transition-all duration-300 ease-eightfold";

// Compose with variants
<button className={`${baseButton} bg-eightfold-teal text-eightfold-navy`}>
```

### 2. Use Data Attributes for States

```tsx
<button data-active={isActive} className="
  data-[active=true]:bg-eightfold-teal
  data-[active=true]:text-white
">
```

### 3. CSS Variable Support

```css
:root {
  --color-teal: theme('colors.eightfold.teal');
  --color-navy: theme('colors.eightfold.navy');
}
```

### 4. Dark Mode First

Always include dark mode classes:
```tsx
<div className="bg-white dark:bg-gray-900">
```

### 5. Responsive Design

```tsx
<div className="
  grid grid-cols-1
  md:grid-cols-2
  lg:grid-cols-3
  gap-6
">
```

---

## Conclusion

These implementation examples provide ready-to-use Tailwind classes that embody the Eightfold.ai design system. Copy and paste these directly into your components, adjusting as needed for your specific use cases.

Remember:
- Always use `eightfold-teal` for primary actions
- Apply `rounded-pill` (112px) for buttons
- Use `rounded-xl` (12px) for cards
- Include hover states with `-translate-y` for interactivity
- Apply `transition-all duration-300 ease-eightfold` for smooth animations
- Support dark mode with `dark:` variants
- Maintain accessibility with focus rings

Happy coding!
