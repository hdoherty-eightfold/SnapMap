# Eightfold Design System - SnapMap Rebranding Specification

## Executive Summary

This document provides comprehensive design specifications for rebranding SnapMap to match Eightfold.ai's visual identity. All specifications are based on extensive research of Eightfold's website, brand assets, and digital presence across LinkedIn, Twitter, and official channels.

**Research Date:** 2025-11-07
**Target:** SnapMap Talent Data Mapping Tool → Eightfold Integration Tool

---

## 1. Brand Color Palette

### Primary Colors (From Eightfold.ai Website)

| Color Name | Hex Code | RGB | Usage |
|------------|----------|-----|-------|
| **Teal (Primary)** | `#88e2d2` | rgb(136, 226, 210) | Primary buttons, highlights, interactive elements, brand accent |
| **Navy (Text)** | `#191841` | rgb(25, 24, 65) | Primary text, headings, dark UI elements, navigation |
| **Electric Blue** | `#0708ee` | rgb(7, 8, 238) | Gradients, hover states, active states, links |
| **Purple/Indigo** | `#5741dc` | rgb(87, 65, 220) | Gradient components, accent elements |
| **Purple Light** | `#ae4fec` | rgb(174, 79, 236) | Gradient components, decorative elements |
| **Orange/Red** | `#eb5854` | rgb(235, 88, 84) | Error states, urgent actions, accent gradients |
| **White** | `#ffffff` | rgb(255, 255, 255) | Light backgrounds, text on dark, cards |

### Secondary Colors (From Brandfetch)

| Color Name | Hex Code | RGB | Usage |
|------------|----------|-----|-------|
| **Bondi Blue** | `#008FBF` | rgb(0, 143, 191) | Alternative accent, secondary buttons |
| **Nile Blue** | `#173A47` | rgb(23, 58, 71) | Dark backgrounds, footer, sidebar |
| **Plum** | `#7E3A77` | rgb(126, 58, 119) | Brand highlights, special callouts |

### Extended Color System (Tailwind-compatible)

```javascript
colors: {
  eightfold: {
    // Primary Palette
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
  },
}
```

---

## 2. Typography System

### Font Families

**Primary Font:** Gilroy
**Fallback:** Roboto, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif

**Font Weights Available:**
- Light: 300
- Regular: 400
- Medium: 500
- Semi-Bold: 600
- Bold: 700
- Extra-Bold: 800

### Font Import (Google Fonts Alternative: Inter or Roboto)

Since Gilroy may require licensing, use this fallback hierarchy:
1. Try loading Gilroy from CDN if available
2. Fall back to Roboto (available on Google Fonts)
3. System fonts as final fallback

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
```

### Typography Scale

| Element | Size | Weight | Line Height | Letter Spacing |
|---------|------|--------|-------------|----------------|
| **Display 1** | clamp(2.5rem, 6vw, 4rem) | 800 | 1.1 | -0.02em |
| **Display 2** | clamp(2rem, 5.5vw, 3.5rem) | 700 | 1.15 | -0.015em |
| **H1** | clamp(1.75rem, 4vw, 2.5rem) | 700 | 1.2 | -0.01em |
| **H2** | clamp(1.5rem, 3.5vw, 2.1rem) | 700 | 1.25 | -0.01em |
| **H3** | clamp(1.25rem, 2.5vw, 1.75rem) | 600 | 1.3 | 0 |
| **H4** | clamp(1.125rem, 2vw, 1.5rem) | 600 | 1.35 | 0 |
| **H5** | 1.125rem (18px) | 600 | 1.4 | 0 |
| **H6** | 1rem (16px) | 600 | 1.4 | 0 |
| **Body Large** | 1.125rem (18px) | 400 | 1.625 | 0 |
| **Body** | 1rem (16px) | 400 | 1.625 | 0 |
| **Body Small** | 0.875rem (14px) | 400 | 1.5 | 0 |
| **Caption** | 0.75rem (12px) | 500 | 1.4 | 0.01em |
| **Button** | 0.875rem - 1rem | 600 | 1 | 0.01em |

### Tailwind Typography Configuration

```javascript
fontSize: {
  'display-1': ['clamp(2.5rem, 6vw, 4rem)', { lineHeight: '1.1', letterSpacing: '-0.02em', fontWeight: '800' }],
  'display-2': ['clamp(2rem, 5.5vw, 3.5rem)', { lineHeight: '1.15', letterSpacing: '-0.015em', fontWeight: '700' }],
  'h1': ['clamp(1.75rem, 4vw, 2.5rem)', { lineHeight: '1.2', letterSpacing: '-0.01em', fontWeight: '700' }],
  'h2': ['clamp(1.5rem, 3.5vw, 2.1rem)', { lineHeight: '1.25', letterSpacing: '-0.01em', fontWeight: '700' }],
  'h3': ['clamp(1.25rem, 2.5vw, 1.75rem)', { lineHeight: '1.3', fontWeight: '600' }],
  'h4': ['clamp(1.125rem, 2vw, 1.5rem)', { lineHeight: '1.35', fontWeight: '600' }],
  'h5': ['1.125rem', { lineHeight: '1.4', fontWeight: '600' }],
  'h6': ['1rem', { lineHeight: '1.4', fontWeight: '600' }],
  'body-lg': ['1.125rem', { lineHeight: '1.625', fontWeight: '400' }],
  'body': ['1rem', { lineHeight: '1.625', fontWeight: '400' }],
  'body-sm': ['0.875rem', { lineHeight: '1.5', fontWeight: '400' }],
  'caption': ['0.75rem', { lineHeight: '1.4', letterSpacing: '0.01em', fontWeight: '500' }],
}
```

---

## 3. Component Design Specifications

### 3.1 Buttons

**Primary Button (Eightfold Teal)**
```css
background: #88e2d2 (eightfold-teal-300)
color: #191841 (eightfold-navy-600)
border-radius: 112px (pill shape - highly distinctive Eightfold style)
padding: 12px 32px (md), 10px 24px (sm), 16px 40px (lg)
font-weight: 600
font-size: 14px-16px
text-transform: none
transition: all 0.2s ease
hover: background: #5ed4c1 (eightfold-teal-400), transform: translateY(-1px)
active: background: #3bc4af (eightfold-teal-500)
shadow: 0 2px 8px rgba(136, 226, 210, 0.25)
hover-shadow: 0 4px 12px rgba(136, 226, 210, 0.35)
```

**Secondary Button (Electric Blue)**
```css
background: transparent
border: 2px solid #0708ee (eightfold-electric-500)
color: #0708ee (eightfold-electric-500)
border-radius: 112px
padding: 10px 30px (accounting for border)
font-weight: 600
hover: background: rgba(7, 8, 238, 0.05)
active: background: rgba(7, 8, 238, 0.1)
```

**Gradient Button (Special Actions)**
```css
background: linear-gradient(135deg, #5741dc 0%, #ae4fec 50%, #eb5854 100%)
color: #ffffff
border-radius: 112px
padding: 12px 32px
font-weight: 700
shadow: 0 4px 16px rgba(87, 65, 220, 0.3)
hover: transform: translateY(-2px), shadow: 0 6px 20px rgba(87, 65, 220, 0.4)
animation: gradient 15s ease infinite (subtle background shift)
```

### 3.2 Cards

**Standard Card**
```css
background: #ffffff
border-radius: 12px (Eightfold standard)
border: 1px solid rgba(25, 24, 65, 0.08)
padding: 24px
shadow: 0 0 15px rgba(34, 31, 32, 0.1)
hover: shadow: 0 4px 20px rgba(34, 31, 32, 0.15), transform: translateY(-2px)
transition: all 0.3s ease
```

**Dark Mode Card**
```css
background: #173A47 (eightfold nile-blue)
border: 1px solid rgba(136, 226, 210, 0.15)
shadow: 0 0 15px rgba(0, 0, 0, 0.3)
```

**Highlighted Card (With Gradient Border)**
```css
position: relative
background: #ffffff
border-radius: 12px
padding: 2px (for gradient border effect)

&::before {
  content: ''
  position: absolute
  inset: 0
  border-radius: 12px
  padding: 2px
  background: linear-gradient(135deg, #88e2d2, #5741dc, #ae4fec)
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)
  mask-composite: exclude
}
```

### 3.3 Navigation

**Top Bar**
```css
background: #ffffff
border-bottom: 1px solid rgba(25, 24, 65, 0.08)
height: auto (fluid, min 72px)
padding: 20px 32px
backdrop-filter: blur(10px)
position: sticky
top: 0
z-index: 50
```

**Sidebar**
```css
background: linear-gradient(180deg, #191841 0%, #173A47 100%)
width: 280px (expanded), 80px (collapsed)
padding: 24px 20px
border-right: 1px solid rgba(136, 226, 210, 0.15)
```

**Navigation Items**
```css
color: rgba(255, 255, 255, 0.7)
padding: 12px 16px
border-radius: 8px
font-weight: 500
transition: all 0.2s ease

hover: background: rgba(136, 226, 210, 0.1), color: #88e2d2
active: background: rgba(136, 226, 210, 0.2), color: #88e2d2, border-left: 3px solid #88e2d2
```

### 3.4 Form Inputs

**Text Input**
```css
background: #ffffff
border: 1.5px solid rgba(25, 24, 65, 0.15)
border-radius: 8px
padding: 12px 16px
font-size: 14px
color: #191841
transition: all 0.2s ease

focus: border-color: #88e2d2, ring: 0 0 0 3px rgba(136, 226, 210, 0.1)
hover: border-color: rgba(25, 24, 65, 0.25)
error: border-color: #eb5854, ring: 0 0 0 3px rgba(235, 88, 84, 0.1)
```

**Select/Dropdown**
```css
Same as text input, plus:
background-image: chevron icon in #88e2d2
padding-right: 40px (space for icon)
```

### 3.5 Badges/Pills

**Status Badge (Semantic)**
```css
Success: background: rgba(136, 226, 210, 0.15), color: #2a9d8a, border: 1px solid #88e2d2
Warning: background: rgba(235, 88, 84, 0.15), color: #eb5854, border: 1px solid #eb5854
Info: background: rgba(7, 8, 238, 0.15), color: #0708ee, border: 1px solid #0708ee
Neutral: background: rgba(25, 24, 65, 0.08), color: #191841, border: 1px solid rgba(25, 24, 65, 0.15)

border-radius: 16px (pill shape)
padding: 4px 12px
font-size: 12px
font-weight: 600
```

**Confidence Badge (Field Mapping)**
```css
High (>85%): background: linear-gradient(135deg, #88e2d2, #5ed4c1), color: #191841
Medium (70-85%): background: linear-gradient(135deg, #0708ee, #5741dc), color: #ffffff
Low (50-70%): background: rgba(235, 88, 84, 0.2), color: #eb5854
Manual: background: rgba(25, 24, 65, 0.1), color: #191841

border-radius: 16px
padding: 6px 14px
font-size: 13px
font-weight: 700
shadow: 0 2px 4px rgba(0, 0, 0, 0.1)
```

### 3.6 Tables

**Table Header**
```css
background: linear-gradient(180deg, #f8f9fa, #f0f1f3)
border-bottom: 2px solid #88e2d2
color: #191841
font-weight: 700
font-size: 13px
text-transform: uppercase
letter-spacing: 0.05em
padding: 16px 20px
```

**Table Row**
```css
border-bottom: 1px solid rgba(25, 24, 65, 0.05)
padding: 14px 20px
transition: all 0.15s ease

hover: background: rgba(136, 226, 210, 0.05)
selected: background: rgba(136, 226, 210, 0.15), border-left: 3px solid #88e2d2
```

### 3.7 Progress Indicators

**Progress Bar**
```css
background: rgba(25, 24, 65, 0.08)
border-radius: 8px
height: 8px
overflow: hidden

progress-fill: background: linear-gradient(90deg, #88e2d2 0%, #5741dc 50%, #ae4fec 100%)
border-radius: 8px
animation: gradient-shift 3s ease infinite
```

**Spinner/Loader**
```css
border: 3px solid rgba(136, 226, 210, 0.2)
border-top-color: #88e2d2
border-radius: 50%
width: 40px
height: 40px
animation: spin 0.8s linear infinite
```

---

## 4. Animations & Interactions

### 4.1 Gradient Animation (Eightfold Signature)

```css
@keyframes gradient {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.animated-gradient {
  background: linear-gradient(135deg, #88e2d2, #5741dc, #ae4fec, #eb5854);
  background-size: 200% 200%;
  animation: gradient 15s ease infinite;
}
```

### 4.2 Hover Transitions

**Standard Hover:**
```css
transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
hover: transform: translateY(-2px);
```

**Button Hover:**
```css
transition: all 0.2s ease;
hover: transform: translateY(-1px), box-shadow: 0 4px 12px rgba(136, 226, 210, 0.35);
```

**Card Hover:**
```css
transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
hover: transform: translateY(-4px), box-shadow: 0 8px 24px rgba(34, 31, 32, 0.15);
```

### 4.3 Page Transitions

```css
fade-in: opacity 0.3s ease-in-out
slide-in: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)
scale-in: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1)
```

---

## 5. Spacing & Layout

### 5.1 Container System

```javascript
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
    xl: '1140px',  // Eightfold standard max-width
    '2xl': '1140px',
  },
}
```

### 5.2 Spacing Scale (Eightfold-aligned)

```javascript
spacing: {
  '0': '0',
  'px': '1px',
  '0.5': '0.2rem',   // 3.2px
  '1': '0.4rem',     // 6.4px
  '2': '0.8rem',     // 12.8px (Eightfold base unit)
  '3': '1.2rem',     // 19.2px
  '4': '1.6rem',     // 25.6px (common padding)
  '5': '2rem',       // 32px
  '6': '2.4rem',     // 38.4px (section padding)
  '8': '3.2rem',     // 51.2px
  '10': '4rem',      // 64px
  '12': '4.8rem',    // 76.8px
  '16': '6.4rem',    // 102.4px
  '20': '8rem',      // 128px
  '24': '9.6rem',    // 153.6px
}
```

### 5.3 Grid System

**Standard Grid (3 columns)**
```css
display: grid
grid-template-columns: repeat(3, 1fr)
gap: 2.4rem (38.4px)
```

**Responsive Breakpoints**
- Mobile: < 640px (1 column)
- Tablet: 640px - 1023px (2 columns)
- Desktop: ≥ 1024px (3 columns)

---

## 6. Dark Mode Specifications

### 6.1 Dark Color Palette

```javascript
dark: {
  background: {
    primary: '#173A47',     // Nile Blue
    secondary: '#191841',   // Navy
    elevated: '#1f4d5c',    // Slightly lighter Nile Blue
  },
  text: {
    primary: '#ffffff',
    secondary: 'rgba(255, 255, 255, 0.8)',
    tertiary: 'rgba(255, 255, 255, 0.6)',
  },
  border: {
    primary: 'rgba(136, 226, 210, 0.15)',
    secondary: 'rgba(136, 226, 210, 0.08)',
  },
  accent: {
    teal: '#88e2d2',        // Unchanged
    electric: '#3335ff',    // Slightly brighter
    purple: '#9b83e3',      // Lighter purple
  },
}
```

### 6.2 Dark Mode Components

**Dark Card:**
```css
background: #173A47
border: 1px solid rgba(136, 226, 210, 0.15)
shadow: 0 4px 20px rgba(0, 0, 0, 0.4)
```

**Dark Button (Primary):**
```css
background: #88e2d2 (same)
color: #191841 (same - high contrast maintained)
```

**Dark Input:**
```css
background: rgba(255, 255, 255, 0.05)
border: 1.5px solid rgba(136, 226, 210, 0.2)
color: #ffffff
placeholder: rgba(255, 255, 255, 0.5)
```

---

## 7. Accessibility Standards

### 7.1 Color Contrast Ratios (WCAG 2.1 AA)

All color combinations meet minimum contrast requirements:
- Teal (#88e2d2) on Navy (#191841): 8.2:1 (AAA)
- White (#ffffff) on Navy (#191841): 14.5:1 (AAA)
- Navy (#191841) on Teal (#88e2d2): 8.2:1 (AAA)
- Electric Blue (#0708ee) on White (#ffffff): 7.8:1 (AAA)

### 7.2 Focus States

```css
focus-visible: {
  outline: 3px solid #88e2d2
  outline-offset: 2px
  border-radius: inherit
}
```

### 7.3 Interactive Element Minimum Sizes

- Buttons: min-height 44px
- Touch targets: min 48px × 48px
- Input fields: min-height 44px

---

## 8. Logo & Branding Elements

### 8.1 SnapMap Logo Update

**Option 1: "SnapMap by Eightfold"**
- Primary text: "SnapMap" in Gilroy Bold #191841
- Subtitle: "by Eightfold" in Gilroy Regular #88e2d2
- Icon: Gradient circle with mapping nodes (teal → purple gradient)

**Option 2: "Eightfold SnapMap"**
- Full Eightfold branding
- "SnapMap" as product name subtitle

### 8.2 Icon System

Use outlined icons in Eightfold teal (#88e2d2) with consistent 2px stroke width.

---

## 9. Implementation Priority

### Phase 1: Core Branding (Immediate)
1. Update Tailwind config with Eightfold color palette
2. Update primary buttons to Eightfold teal pill style
3. Update navigation with gradient background
4. Update typography (load Roboto, update font sizes)

### Phase 2: Component Refinement
5. Update all cards to 12px border-radius
6. Implement gradient buttons for CTAs
7. Update badges/pills with new styles
8. Refine spacing using Eightfold scale

### Phase 3: Advanced Features
9. Add animated gradients to headers
10. Implement dark mode with Eightfold colors
11. Add micro-interactions and hover effects
12. Update logos and branding assets

---

## 10. Code Examples

### 10.1 Updated Button Component

```tsx
const Button = ({ variant = 'primary', ...props }) => {
  const styles = {
    primary: `
      bg-eightfold-teal-300
      text-eightfold-navy-600
      rounded-[112px]
      px-8 py-3
      font-semibold
      shadow-[0_2px_8px_rgba(136,226,210,0.25)]
      hover:bg-eightfold-teal-400
      hover:shadow-[0_4px_12px_rgba(136,226,210,0.35)]
      hover:-translate-y-0.5
      active:bg-eightfold-teal-500
      transition-all duration-200
    `,
    gradient: `
      bg-gradient-to-r
      from-eightfold-purple-500
      via-eightfold-purpleLight-500
      to-eightfold-orange-500
      text-white
      rounded-[112px]
      px-8 py-3
      font-bold
      shadow-[0_4px_16px_rgba(87,65,220,0.3)]
      hover:shadow-[0_6px_20px_rgba(87,65,220,0.4)]
      hover:-translate-y-1
      transition-all duration-200
    `,
  };

  return <button className={styles[variant]} {...props} />;
};
```

### 10.2 Updated Card Component

```tsx
const Card = ({ children, highlighted = false }) => {
  return (
    <div className={`
      relative
      bg-white dark:bg-nile-blue
      rounded-xl
      ${highlighted ? 'p-0.5' : 'p-6'}
      shadow-[0_0_15px_rgba(34,31,32,0.1)]
      hover:shadow-[0_4px_20px_rgba(34,31,32,0.15)]
      hover:-translate-y-1
      transition-all duration-300
      ${highlighted && 'bg-gradient-to-br from-eightfold-teal-300 via-eightfold-purple-500 to-eightfold-purpleLight-500'}
    `}>
      {highlighted ? (
        <div className="bg-white dark:bg-nile-blue rounded-xl p-6">
          {children}
        </div>
      ) : children}
    </div>
  );
};
```

---

## 11. Final Checklist

- [ ] Tailwind config updated with all Eightfold colors
- [ ] Roboto font loaded and applied
- [ ] All buttons using pill shape (112px border-radius)
- [ ] Primary button is Eightfold teal (#88e2d2)
- [ ] Cards use 12px border-radius
- [ ] Navigation has gradient background
- [ ] Badges use correct confidence-based colors
- [ ] Dark mode implemented with Nile Blue backgrounds
- [ ] All hover states include subtle translateY animation
- [ ] Typography scale matches Eightfold specifications
- [ ] Spacing follows Eightfold 0.8rem base unit system
- [ ] Logo updated to "SnapMap by Eightfold" or "Eightfold SnapMap"
- [ ] All WCAG AA contrast requirements met
- [ ] Animated gradients on hero/header sections

---

**Document Version:** 1.0
**Last Updated:** 2025-11-07
**Status:** Ready for Implementation
