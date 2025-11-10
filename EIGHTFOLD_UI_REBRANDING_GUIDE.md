# SnapMap UI/UX Rebranding Guide
## Eightfold.ai Design System Integration

**Document Version:** 1.0
**Last Updated:** November 7, 2025
**Purpose:** Complete design specification for rebranding SnapMap to match Eightfold.ai's visual identity

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Brand Foundation](#brand-foundation)
3. [Color System](#color-system)
4. [Typography System](#typography-system)
5. [Component Library](#component-library)
6. [Spacing & Layout](#spacing-and-layout)
7. [Animation & Interactions](#animation-and-interactions)
8. [Responsive Design](#responsive-design)
9. [Implementation Guide](#implementation-guide)
10. [Design Rationale](#design-rationale)

---

## Executive Summary

SnapMap is a talent data mapping and transformation tool that enables seamless integration of HR data from various sources into Eightfold.ai's Talent Intelligence Platform. This rebranding guide ensures SnapMap feels like an authentic Eightfold product while maintaining its core functionality for CSV/Excel upload, intelligent field mapping, and data transformation.

**Design Philosophy:**
- Modern, gradient-heavy design matching Eightfold's visual language
- Clean, minimalist interfaces with vibrant accent colors
- Sophisticated yet approachable for HR professionals
- Tech-forward aesthetic emphasizing AI-powered capabilities

---

## Brand Foundation

### Eightfold.ai Brand Identity

**Brand Essence:** AI-powered talent intelligence combining innovation with reliability

**Visual Characteristics:**
- Modern tech aesthetic with vibrant gradients
- Clean, spacious layouts with purposeful white space
- Dynamic visual elements suggesting intelligence and movement
- Professional yet approachable tone

**Key Differentiators:**
- Heavy use of multi-directional gradients
- Gilroy custom typography for premium feel
- Rounded, pill-shaped buttons for friendly interaction
- Teal as primary accent for energy and innovation

---

## Color System

### Primary Palette

```css
/* Core Brand Colors */
--eightfold-teal: #88e2d2;        /* Primary accent, CTAs, highlights */
--eightfold-navy: #191841;        /* Headers, primary text, dark backgrounds */
--eightfold-electric-blue: #0708ee; /* Interactive elements, links */
--eightfold-quantum-indigo: #5741dc; /* Gradient component */
--eightfold-smart-orange: #eb5854;  /* Accent, gradient component */
```

### Secondary Palette

```css
/* Supporting Colors */
--eightfold-deep-magenta: #a1378b;  /* Secondary gradients */
--eightfold-purple-light: #ae4fec;  /* Gradient component */
--eightfold-fusion-gold: #f8a456;   /* Accent highlights */
```

### Neutral Palette

```css
/* Neutrals */
--neutral-white: #ffffff;
--neutral-lightest: #f8f8f8;       /* Subtle backgrounds */
--neutral-light: #e5e7eb;          /* Borders, dividers */
--neutral-medium: #9ca3af;         /* Secondary text */
--neutral-dark: #484b58;           /* Body text on light */
--neutral-darkest: #191841;        /* Headers, dark mode bg */
```

### Semantic Colors

```css
/* Status & Feedback */
--success-light: #d1fae5;
--success: #10b981;
--success-dark: #059669;

--warning-light: #fef3c7;
--warning: #f59e0b;
--warning-dark: #d97706;

--error-light: #fee2e2;
--error: #ef4444;
--error-dark: #dc2626;

--info-light: #dbeafe;
--info: #3b82f6;
--info-dark: #2563eb;
```

### Gradient Definitions

```css
/* Primary Gradients */
--gradient-primary: linear-gradient(135deg, #88e2d2 0%, #5741dc 50%, #0708ee 100%);
--gradient-warm: linear-gradient(135deg, #eb5854 0%, #f8a456 100%);
--gradient-cool: linear-gradient(135deg, #0708ee 0%, #88e2d2 100%);
--gradient-hero: linear-gradient(135deg, #191841 0%, #5741dc 50%, #0708ee 100%);

/* Multi-directional Gradients (Complex) */
--gradient-complex: radial-gradient(circle at 20% 50%, #eb5854 0%, transparent 50%),
                     radial-gradient(circle at 80% 50%, #0708ee 0%, transparent 50%),
                     linear-gradient(135deg, #5741dc 0%, #191841 100%);

/* Overlay Gradients */
--gradient-overlay-dark: linear-gradient(180deg, rgba(25, 24, 65, 0) 0%, rgba(25, 24, 65, 0.8) 100%);
--gradient-overlay-light: linear-gradient(180deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.6) 100%);
```

### Color Usage Guidelines

#### Where to Use Each Color

**Teal (#88e2d2) - Primary Accent**
- Primary action buttons
- Active states in navigation
- Success indicators
- Hover states on interactive elements
- Progress bars and loading indicators
- Badge accents for AI-powered features

**Navy (#191841) - Primary Dark**
- Main headers and page titles
- Dark mode primary background
- Footer backgrounds
- Sidebar in dark mode
- Text on light backgrounds (headings)

**Electric Blue (#0708ee) - Interactive**
- Links and hyperlinks
- Secondary buttons
- Focus states
- Interactive icon highlights
- Notification badges

**Quantum Indigo (#5741dc) - Gradient Component**
- Gradient backgrounds (heroes, cards)
- Accent elements in complex designs
- Hover states with gradients
- Background patterns

**Smart Orange (#eb5854) - Accent**
- Gradient components
- Warning/alert accents (when not semantic)
- Hot spots in data visualizations
- Attention-grabbing elements

#### Color Application Matrix

| Element Type | Light Mode | Dark Mode | Hover State |
|-------------|-----------|-----------|-------------|
| **Primary Button** | Teal bg + White text | Teal bg + Navy text | Darker teal |
| **Secondary Button** | White bg + Teal border | Navy bg + Teal border | Teal bg |
| **Card Background** | White | #1f1f3a (lighter navy) | Subtle lift |
| **Page Background** | #f8f8f8 | #191841 | N/A |
| **Primary Text** | #484b58 (dark gray) | White | N/A |
| **Secondary Text** | #9ca3af | #d1d5db | N/A |
| **Border/Divider** | #e5e7eb | #374151 | N/A |
| **Active Nav Item** | Teal bg + Navy text | Teal/30% opacity + Teal text | N/A |

---

## Typography System

### Font Family

**Primary Font:** Gilroy (weights: 400, 500, 600, 700, 800)
**Fallback Stack:** -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif

**Implementation Note:** Gilroy is a premium font. If licensing is not available, use these alternatives:
- **Best Alternative:** Montserrat (Google Fonts - geometric, modern)
- **Secondary Alternative:** Inter (Google Fonts - optimized for screens)
- **Fallback:** System fonts as listed above

### Type Scale

```css
/* Responsive Typography using clamp() */
--font-size-h1: clamp(2rem, 5.5vw, 3.5rem);        /* 32px - 56px */
--font-size-h2: clamp(1.6rem, 3.8vw, 2.5rem);      /* 25.6px - 40px */
--font-size-h3: clamp(1.4rem, 2.5vw, 2rem);        /* 22.4px - 32px */
--font-size-h4: clamp(1.2rem, 2vw, 1.5rem);        /* 19.2px - 24px */
--font-size-h5: 1.125rem;                           /* 18px */
--font-size-h6: 1rem;                               /* 16px */

--font-size-body-lg: 1.125rem;                      /* 18px */
--font-size-body: 1rem;                             /* 16px */
--font-size-body-sm: 0.875rem;                      /* 14px */
--font-size-caption: 0.75rem;                       /* 12px */

/* Line Heights */
--line-height-tight: 1.1;
--line-height-normal: 1.5;
--line-height-relaxed: 1.625;

/* Letter Spacing */
--letter-spacing-tight: -0.02em;
--letter-spacing-normal: 0;
--letter-spacing-wide: 0.025em;
--letter-spacing-wider: 0.05em;
```

### Typography Hierarchy

#### Page Headers (H1)
```css
.page-header {
  font-size: clamp(2rem, 5.5vw, 3.5rem);
  font-weight: 700;
  line-height: 1.1;
  letter-spacing: -0.02em;
  color: var(--eightfold-navy);
  margin-bottom: 1rem;
}

.dark .page-header {
  color: var(--neutral-white);
}
```

#### Section Headers (H2)
```css
.section-header {
  font-size: clamp(1.6rem, 3.8vw, 2.5rem);
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: -0.01em;
  color: var(--eightfold-navy);
  margin-bottom: 0.75rem;
}
```

#### Card Headers (H3)
```css
.card-header {
  font-size: clamp(1.4rem, 2.5vw, 2rem);
  font-weight: 600;
  line-height: 1.3;
  color: var(--eightfold-navy);
  margin-bottom: 0.5rem;
}
```

#### Component Titles (H4-H6)
```css
.component-title {
  font-size: 1.125rem;
  font-weight: 600;
  line-height: 1.4;
  color: var(--neutral-dark);
}

.component-subtitle {
  font-size: 1rem;
  font-weight: 500;
  line-height: 1.5;
  color: var(--neutral-dark);
}
```

#### Body Text
```css
.body-text {
  font-size: 1rem;
  font-weight: 400;
  line-height: 1.625;
  color: var(--neutral-dark);
}

.body-text-large {
  font-size: 1.125rem;
  font-weight: 400;
  line-height: 1.625;
  color: var(--neutral-dark);
}

.body-text-small {
  font-size: 0.875rem;
  font-weight: 400;
  line-height: 1.5;
  color: var(--neutral-medium);
}
```

#### Labels & Captions
```css
.label {
  font-size: 0.875rem;
  font-weight: 600;
  line-height: 1.4;
  letter-spacing: 0.025em;
  text-transform: uppercase;
  color: var(--neutral-dark);
}

.caption {
  font-size: 0.75rem;
  font-weight: 400;
  line-height: 1.5;
  color: var(--neutral-medium);
}
```

#### Buttons
```css
.button-text {
  font-size: 1rem;
  font-weight: 600;
  line-height: 1.5;
  letter-spacing: 0.025em;
}

.button-text-small {
  font-size: 0.875rem;
  font-weight: 600;
  line-height: 1.4;
}
```

### Font Loading Strategy

```css
/* Ensure smooth font loading */
@font-face {
  font-family: 'Gilroy';
  src: url('/fonts/Gilroy-Regular.woff2') format('woff2');
  font-weight: 400;
  font-display: swap;
}

@font-face {
  font-family: 'Gilroy';
  src: url('/fonts/Gilroy-Medium.woff2') format('woff2');
  font-weight: 500;
  font-display: swap;
}

@font-face {
  font-family: 'Gilroy';
  src: url('/fonts/Gilroy-SemiBold.woff2') format('woff2');
  font-weight: 600;
  font-display: swap;
}

@font-face {
  font-family: 'Gilroy';
  src: url('/fonts/Gilroy-Bold.woff2') format('woff2');
  font-weight: 700;
  font-display: swap;
}

@font-face {
  font-family: 'Gilroy';
  src: url('/fonts/Gilroy-ExtraBold.woff2') format('woff2');
  font-weight: 800;
  font-display: swap;
}
```

---

## Component Library

### Buttons

#### Primary Button (Teal)
```css
.btn-primary {
  /* Core Styles */
  background: var(--eightfold-teal);
  color: var(--eightfold-navy);
  font-size: 1rem;
  font-weight: 600;
  padding: 12px 40px;
  border-radius: 112px; /* Pill shape */
  border: none;

  /* Interactive States */
  transition: all 0.3s cubic-bezier(0.87, 0, 0.13, 1);
  cursor: pointer;

  /* Shadow */
  box-shadow: 0 2px 8px rgba(136, 226, 210, 0.2);
}

.btn-primary:hover {
  background: #6fd5c4;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(136, 226, 210, 0.3);
}

.btn-primary:active {
  transform: translateY(0);
  box-shadow: 0 1px 4px rgba(136, 226, 210, 0.2);
}

.btn-primary:disabled {
  background: #e5e7eb;
  color: #9ca3af;
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

/* Dark Mode */
.dark .btn-primary {
  color: var(--eightfold-navy);
}
```

#### Secondary Button (Outline)
```css
.btn-secondary {
  background: transparent;
  color: var(--eightfold-teal);
  font-size: 1rem;
  font-weight: 600;
  padding: 12px 40px;
  border-radius: 112px;
  border: 2px solid var(--eightfold-teal);
  transition: all 0.3s cubic-bezier(0.87, 0, 0.13, 1);
}

.btn-secondary:hover {
  background: var(--eightfold-teal);
  color: var(--eightfold-navy);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(136, 226, 210, 0.2);
}
```

#### Gradient CTA Button
```css
.btn-gradient {
  background: linear-gradient(135deg, #88e2d2 0%, #5741dc 50%, #0708ee 100%);
  color: white;
  font-size: 1.125rem;
  font-weight: 700;
  padding: 14px 48px;
  border-radius: 112px;
  border: none;
  box-shadow: 0 4px 16px rgba(87, 65, 220, 0.3);
  transition: all 0.3s cubic-bezier(0.87, 0, 0.13, 1);
}

.btn-gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(87, 65, 220, 0.4);
}
```

#### Ghost Button
```css
.btn-ghost {
  background: transparent;
  color: var(--neutral-dark);
  font-size: 1rem;
  font-weight: 500;
  padding: 8px 16px;
  border-radius: 8px;
  border: none;
  transition: all 0.2s ease;
}

.btn-ghost:hover {
  background: rgba(136, 226, 210, 0.1);
  color: var(--eightfold-teal);
}
```

#### Button Sizes
```css
/* Small */
.btn-sm {
  padding: 8px 24px;
  font-size: 0.875rem;
  border-radius: 100px;
}

/* Medium (Default) */
.btn-md {
  padding: 12px 40px;
  font-size: 1rem;
  border-radius: 112px;
}

/* Large */
.btn-lg {
  padding: 16px 56px;
  font-size: 1.125rem;
  border-radius: 112px;
}
```

### Cards

#### Standard Card
```css
.card {
  /* Core Styles */
  background: white;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 0 15px rgba(34, 31, 32, 0.1);
  border: 1px solid rgba(229, 231, 235, 0.8);

  /* Transition */
  transition: all 0.3s cubic-bezier(0.87, 0, 0.13, 1);
}

.card:hover {
  box-shadow: 0 4px 24px rgba(34, 31, 32, 0.12);
  transform: translateY(-4px);
}

/* Dark Mode */
.dark .card {
  background: #1f1f3a;
  border-color: rgba(87, 65, 220, 0.2);
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.3);
}
```

#### Feature Card with Gradient
```css
.card-feature {
  background: linear-gradient(135deg, #191841 0%, #5741dc 100%);
  border-radius: 12px;
  padding: 32px;
  color: white;
  position: relative;
  overflow: hidden;
}

.card-feature::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(136, 226, 210, 0.2) 0%, transparent 70%);
  border-radius: 50%;
}
```

#### Card with Backdrop Blur
```css
.card-blur {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 12px;
  padding: 24px;
}

.dark .card-blur {
  background: rgba(31, 31, 58, 0.8);
  border-color: rgba(87, 65, 220, 0.3);
}
```

### Badges

```css
.badge {
  display: inline-flex;
  align-items: center;
  padding: 6px 16px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-radius: 100px;
  line-height: 1;
}

.badge-success {
  background: var(--success-light);
  color: var(--success-dark);
}

.badge-warning {
  background: var(--warning-light);
  color: var(--warning-dark);
}

.badge-error {
  background: var(--error-light);
  color: var(--error-dark);
}

.badge-primary {
  background: rgba(136, 226, 210, 0.2);
  color: var(--eightfold-teal);
  border: 1px solid var(--eightfold-teal);
}

.badge-ai {
  background: linear-gradient(135deg, #88e2d2 0%, #5741dc 100%);
  color: white;
}
```

### Form Inputs

#### Text Input
```css
.input {
  width: 100%;
  padding: 12px 16px;
  font-size: 1rem;
  font-weight: 400;
  color: var(--neutral-dark);
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.input:focus {
  outline: none;
  border-color: var(--eightfold-teal);
  box-shadow: 0 0 0 3px rgba(136, 226, 210, 0.1);
}

.input:disabled {
  background: #f8f8f8;
  cursor: not-allowed;
}

/* Dark Mode */
.dark .input {
  background: #1f1f3a;
  border-color: #374151;
  color: white;
}
```

#### Select Dropdown
```css
.select {
  width: 100%;
  padding: 12px 16px;
  font-size: 1rem;
  font-weight: 500;
  color: var(--neutral-dark);
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3E%3Cpath stroke='%236B7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3E%3C/svg%3E");
  background-position: right 12px center;
  background-repeat: no-repeat;
  background-size: 20px;
  padding-right: 40px;
}

.select:hover {
  border-color: var(--eightfold-teal);
}

.select:focus {
  outline: none;
  border-color: var(--eightfold-teal);
  box-shadow: 0 0 0 3px rgba(136, 226, 210, 0.1);
}
```

#### File Upload Zone
```css
.upload-zone {
  border: 2px dashed #e5e7eb;
  border-radius: 12px;
  padding: 48px 32px;
  text-align: center;
  background: white;
  transition: all 0.3s ease;
  cursor: pointer;
}

.upload-zone:hover {
  border-color: var(--eightfold-teal);
  background: rgba(136, 226, 210, 0.05);
}

.upload-zone.dragging {
  border-color: var(--eightfold-teal);
  background: rgba(136, 226, 210, 0.1);
  transform: scale(1.02);
}

.upload-zone.success {
  border-color: var(--success);
  background: var(--success-light);
}

.upload-zone.error {
  border-color: var(--error);
  background: var(--error-light);
}
```

### Navigation

#### Sidebar Navigation
```css
.sidebar {
  width: 256px;
  height: 100vh;
  background: white;
  border-right: 1px solid #e5e7eb;
  transition: all 0.3s cubic-bezier(0.87, 0, 0.13, 1);
}

.sidebar.collapsed {
  width: 80px;
}

.dark .sidebar {
  background: #191841;
  border-color: rgba(87, 65, 220, 0.2);
}

.nav-item {
  padding: 12px 16px;
  margin: 4px 8px;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--neutral-dark);
  transition: all 0.2s ease;
  cursor: pointer;
  position: relative;
}

.nav-item:hover {
  background: rgba(136, 226, 210, 0.1);
  color: var(--eightfold-teal);
}

.nav-item.active {
  background: rgba(136, 226, 210, 0.15);
  color: var(--eightfold-teal);
  font-weight: 600;
}

.nav-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 24px;
  background: var(--eightfold-teal);
  border-radius: 0 2px 2px 0;
}
```

### Tables

```css
.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.table thead {
  background: var(--neutral-lightest);
  border-bottom: 2px solid #e5e7eb;
}

.table th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--neutral-dark);
}

.table td {
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
  color: var(--neutral-dark);
}

.table tr:hover {
  background: rgba(136, 226, 210, 0.05);
}

.dark .table thead {
  background: #1f1f3a;
  border-color: #374151;
}

.dark .table td {
  border-color: #374151;
  color: white;
}
```

### Modals

```css
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(25, 24, 65, 0.7);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 12px;
  padding: 32px;
  max-width: 600px;
  width: 90%;
  box-shadow: 0 20px 60px rgba(25, 24, 65, 0.3);
  transform: scale(0.9);
  opacity: 0;
  transition: all 0.3s cubic-bezier(0.87, 0, 0.13, 1);
}

.modal.active {
  transform: scale(1);
  opacity: 1;
}

.dark .modal {
  background: #1f1f3a;
}
```

### Tooltips

```css
.tooltip {
  position: relative;
}

.tooltip::after {
  content: attr(data-tooltip);
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%) translateY(-8px);
  padding: 8px 12px;
  background: var(--eightfold-navy);
  color: white;
  font-size: 0.75rem;
  font-weight: 500;
  border-radius: 6px;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: all 0.2s ease;
}

.tooltip:hover::after {
  opacity: 1;
  transform: translateX(-50%) translateY(-4px);
}
```

### Progress Indicators

#### Linear Progress Bar
```css
.progress-bar {
  width: 100%;
  height: 8px;
  background: #e5e7eb;
  border-radius: 100px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #88e2d2 0%, #5741dc 100%);
  border-radius: 100px;
  transition: width 0.3s ease;
}
```

#### Circular Loading Spinner
```css
.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(136, 226, 210, 0.2);
  border-top-color: var(--eightfold-teal);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

---

## Spacing and Layout

### Spacing Scale

```css
/* Base unit: 4px */
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
--space-20: 5rem;     /* 80px */
--space-24: 6rem;     /* 96px */
```

### Layout Grid

```css
/* Container System */
.container {
  width: 100%;
  max-width: 1140px;
  margin: 0 auto;
  padding: 0 1.6rem;
}

.container-fluid {
  width: 100%;
  padding: 0 1.6rem;
}

.container-narrow {
  max-width: 768px;
  margin: 0 auto;
  padding: 0 1.6rem;
}

/* Grid System */
.grid {
  display: grid;
  gap: var(--space-6);
}

.grid-2 {
  grid-template-columns: repeat(2, 1fr);
}

.grid-3 {
  grid-template-columns: repeat(3, 1fr);
}

.grid-4 {
  grid-template-columns: repeat(4, 1fr);
}

/* Responsive Grid */
@media (max-width: 768px) {
  .grid-2, .grid-3, .grid-4 {
    grid-template-columns: 1fr;
  }
}

/* Flexbox Utilities */
.flex {
  display: flex;
}

.flex-col {
  flex-direction: column;
}

.items-center {
  align-items: center;
}

.justify-between {
  justify-content: space-between;
}

.gap-2 { gap: var(--space-2); }
.gap-4 { gap: var(--space-4); }
.gap-6 { gap: var(--space-6); }
.gap-8 { gap: var(--space-8); }
```

### Component Spacing Guidelines

| Component | Padding | Margin | Gap |
|-----------|---------|--------|-----|
| **Card** | 32px all sides | 24px bottom | N/A |
| **Button** | 12px vertical, 40px horizontal | 8px right (in groups) | N/A |
| **Input** | 12px all sides | 16px bottom | N/A |
| **Section** | 64px vertical | N/A | N/A |
| **Sidebar Item** | 12px all sides | 4px vertical | 12px (icon-text) |
| **Modal** | 32px all sides | N/A | N/A |
| **Table Cell** | 16px all sides | N/A | N/A |

---

## Animation and Interactions

### Transition Timing

```css
/* Eightfold Standard Easing */
--ease-eightfold: cubic-bezier(0.87, 0, 0.13, 1);

/* Standard Durations */
--duration-fast: 0.15s;
--duration-normal: 0.3s;
--duration-slow: 0.5s;
```

### Micro-interactions

#### Hover Lift Effect
```css
.hover-lift {
  transition: transform 0.3s var(--ease-eightfold),
              box-shadow 0.3s var(--ease-eightfold);
}

.hover-lift:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(25, 24, 65, 0.15);
}
```

#### Button Press Effect
```css
.button-press {
  transition: transform 0.1s ease;
}

.button-press:active {
  transform: scale(0.95);
}
```

#### Fade In Animation
```css
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in {
  animation: fadeIn 0.5s var(--ease-eightfold) forwards;
}
```

#### Slide In from Right (Toast)
```css
@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.slide-in-right {
  animation: slideInRight 0.3s var(--ease-eightfold) forwards;
}
```

#### Gradient Animation
```css
@keyframes gradientShift {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.animated-gradient {
  background: linear-gradient(
    -45deg,
    #88e2d2,
    #5741dc,
    #0708ee,
    #eb5854
  );
  background-size: 400% 400%;
  animation: gradientShift 15s ease infinite;
}
```

#### Loading Pulse
```css
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.loading-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
```

### Focus States

```css
/* Accessible Focus Rings */
.focus-ring {
  outline: none;
  transition: box-shadow 0.2s ease;
}

.focus-ring:focus-visible {
  box-shadow: 0 0 0 3px rgba(136, 226, 210, 0.4);
  border-color: var(--eightfold-teal);
}

/* Skip to Content Link */
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: var(--eightfold-navy);
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  z-index: 100;
}

.skip-link:focus {
  top: 8px;
}
```

---

## Responsive Design

### Breakpoints

```css
/* Mobile First Approach */
--breakpoint-sm: 640px;   /* Small devices (landscape phones) */
--breakpoint-md: 768px;   /* Medium devices (tablets) */
--breakpoint-lg: 1024px;  /* Large devices (laptops) */
--breakpoint-xl: 1280px;  /* Extra large devices (desktops) */
--breakpoint-2xl: 1536px; /* 2X large devices (large desktops) */
```

### Responsive Typography

Use `clamp()` for fluid typography that scales smoothly:

```css
/* Example: H1 scales from 32px to 56px */
font-size: clamp(2rem, 5.5vw, 3.5rem);

/* Calculation: clamp(min, preferred, max) */
/* min: 2rem (32px) - mobile */
/* preferred: 5.5vw - scales with viewport */
/* max: 3.5rem (56px) - desktop */
```

### Responsive Layout Patterns

#### Stack on Mobile, Grid on Desktop
```css
.responsive-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

@media (min-width: 768px) {
  .responsive-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .responsive-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

#### Sidebar Collapse
```css
.sidebar {
  width: 256px;
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
}

@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }

  .sidebar.open {
    transform: translateX(0);
  }
}
```

#### Mobile-First Container
```css
.container {
  width: 100%;
  padding: 0 1rem;
}

@media (min-width: 640px) {
  .container {
    padding: 0 1.5rem;
  }
}

@media (min-width: 1024px) {
  .container {
    max-width: 1140px;
    margin: 0 auto;
    padding: 0 1.6rem;
  }
}
```

### Touch Targets

Ensure all interactive elements meet minimum touch target sizes:

```css
/* Minimum 44x44px for touch targets */
.touch-target {
  min-width: 44px;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
```

---

## Implementation Guide

### Tailwind CSS Configuration

Update your `tailwind.config.js` with Eightfold brand tokens:

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
      },
      fontSize: {
        'h1': 'clamp(2rem, 5.5vw, 3.5rem)',
        'h2': 'clamp(1.6rem, 3.8vw, 2.5rem)',
        'h3': 'clamp(1.4rem, 2.5vw, 2rem)',
        'h4': 'clamp(1.2rem, 2vw, 1.5rem)',
      },
      borderRadius: {
        'pill': '112px',
      },
      boxShadow: {
        'card': '0 0 15px rgba(34, 31, 32, 0.1)',
        'card-hover': '0 4px 24px rgba(34, 31, 32, 0.12)',
        'button': '0 2px 8px rgba(136, 226, 210, 0.2)',
        'button-hover': '0 4px 12px rgba(136, 226, 210, 0.3)',
      },
      transitionTimingFunction: {
        'eightfold': 'cubic-bezier(0.87, 0, 0.13, 1)',
      },
      animation: {
        'gradient-shift': 'gradientShift 15s ease infinite',
        'fade-in': 'fadeIn 0.5s cubic-bezier(0.87, 0, 0.13, 1) forwards',
        'slide-in-right': 'slideInRight 0.3s cubic-bezier(0.87, 0, 0.13, 1) forwards',
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
      },
    },
  },
  plugins: [],
}
```

### Component Implementation Examples

#### Button Component (React + Tailwind)

```tsx
import React, { ButtonHTMLAttributes } from 'react';
import { Loader2 } from 'lucide-react';

type ButtonVariant = 'primary' | 'secondary' | 'gradient' | 'ghost';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  children: React.ReactNode;
}

const variantClasses: Record<ButtonVariant, string> = {
  primary: 'bg-eightfold-teal text-eightfold-navy hover:bg-primary-400 shadow-button hover:shadow-button-hover',
  secondary: 'border-2 border-eightfold-teal text-eightfold-teal hover:bg-eightfold-teal hover:text-eightfold-navy',
  gradient: 'bg-gradient-to-r from-eightfold-teal via-eightfold-quantum-indigo to-accent-500 text-white shadow-lg',
  ghost: 'text-gray-700 hover:bg-eightfold-teal/10 hover:text-eightfold-teal',
};

const sizeClasses: Record<ButtonSize, string> = {
  sm: 'px-6 py-2 text-sm rounded-pill',
  md: 'px-10 py-3 text-base rounded-pill',
  lg: 'px-14 py-4 text-lg rounded-pill',
};

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  isLoading = false,
  leftIcon,
  rightIcon,
  disabled,
  className = '',
  children,
  ...props
}) => {
  return (
    <button
      className={`
        inline-flex items-center justify-center gap-2 font-semibold
        transition-all duration-300 ease-eightfold
        focus:outline-none focus:ring-3 focus:ring-eightfold-teal/40
        disabled:opacity-60 disabled:cursor-not-allowed
        hover:-translate-y-0.5 active:translate-y-0
        ${variantClasses[variant]}
        ${sizeClasses[size]}
        ${className}
      `}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <Loader2 className="h-4 w-4 animate-spin" />
      ) : leftIcon ? (
        <span>{leftIcon}</span>
      ) : null}
      {children}
      {!isLoading && rightIcon && <span>{rightIcon}</span>}
    </button>
  );
};
```

#### Card Component (React + Tailwind)

```tsx
import React, { HTMLAttributes } from 'react';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  hover?: boolean;
  gradient?: boolean;
  blur?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  hover = false,
  gradient = false,
  blur = false,
  className = '',
  ...props
}) => {
  const baseClasses = 'rounded-xl p-8 transition-all duration-300 ease-eightfold';

  const variantClasses = gradient
    ? 'bg-gradient-to-br from-eightfold-navy to-eightfold-quantum-indigo text-white'
    : blur
    ? 'bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border border-white/30 dark:border-gray-700/30'
    : 'bg-white dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 shadow-card';

  const hoverClasses = hover
    ? 'hover:shadow-card-hover hover:-translate-y-1 cursor-pointer'
    : '';

  return (
    <div
      className={`${baseClasses} ${variantClasses} ${hoverClasses} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

export const CardHeader: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="mb-4 pb-4 border-b border-gray-200 dark:border-gray-700">
    {children}
  </div>
);

export const CardTitle: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <h3 className="text-2xl font-bold text-eightfold-navy dark:text-white">
    {children}
  </h3>
);
```

### CSS Custom Properties Setup

Add to your main CSS file:

```css
:root {
  /* Colors */
  --eightfold-teal: #88e2d2;
  --eightfold-navy: #191841;
  --eightfold-electric-blue: #0708ee;
  --eightfold-quantum-indigo: #5741dc;
  --eightfold-smart-orange: #eb5854;

  /* Spacing */
  --space-unit: 0.25rem;

  /* Transitions */
  --ease-eightfold: cubic-bezier(0.87, 0, 0.13, 1);
  --duration-normal: 0.3s;

  /* Shadows */
  --shadow-card: 0 0 15px rgba(34, 31, 32, 0.1);
  --shadow-card-hover: 0 4px 24px rgba(34, 31, 32, 0.12);
}

/* Dark mode overrides */
.dark {
  --card-bg: #1f1f3a;
  --text-primary: #ffffff;
  --text-secondary: #d1d5db;
  --border-color: rgba(87, 65, 220, 0.2);
}
```

---

## Design Rationale

### Color Choices

**Teal (#88e2d2) as Primary Accent**
- Represents innovation, energy, and forward-thinking
- Stands out against navy backgrounds
- Accessible contrast ratios (WCAG AA compliant)
- Distinctive from typical corporate blues

**Navy (#191841) as Foundation**
- Conveys professionalism and trust
- Provides strong contrast for white text
- Creates sophisticated dark mode experience
- Grounds the vibrant accent colors

**Electric Blue (#0708ee) for Interaction**
- High visibility for clickable elements
- Creates sense of digital intelligence
- Complements teal without competing
- Traditional "link blue" evolved

**Gradients for Visual Interest**
- Multi-color gradients suggest AI intelligence
- Creates depth and dimensionality
- Differentiates from flat corporate designs
- Draws attention to key areas

### Typography Rationale

**Gilroy Font Family**
- Geometric sans-serif feels modern and technical
- Multiple weights provide clear hierarchy
- Rounded letterforms feel approachable
- Distinctive personality vs. standard web fonts

**Fluid Typography (clamp)**
- Responsive without breakpoints
- Smooth scaling across all screen sizes
- Maintains readability at any viewport
- Reduces CSS complexity

### Component Design Decisions

**Pill-Shaped Buttons (112px border-radius)**
- Friendly, approachable aesthetic
- Distinctive from standard rounded corners
- Encourages action through softness
- Consistent with modern design trends

**12px Card Border Radius**
- Subtle rounding feels polished
- Not too playful for enterprise context
- Consistent across all card components
- Balances modern with professional

**Generous Padding (32px)**
- Creates breathing room for content
- Feels premium and considered
- Improves scannability
- Aligns with Eightfold's spacious layouts

**Hover Lift Effects**
- Provides tactile feedback
- Suggests interactivity
- Creates sense of layering
- Feels responsive and alive

### Accessibility Considerations

**Color Contrast**
- All text meets WCAG AA standards (4.5:1 minimum)
- Important elements meet AAA standards (7:1)
- Dark mode maintains same standards

**Focus Indicators**
- Visible focus rings on all interactive elements
- 3px offset provides clear separation
- Teal color matches brand while standing out

**Touch Targets**
- Minimum 44x44px for mobile interactions
- Adequate spacing between clickable elements
- Large buttons for primary actions

**Motion Sensitivity**
- Animations can be disabled via `prefers-reduced-motion`
- No auto-playing animations
- Smooth, purposeful transitions only

### SnapMap-Specific Applications

**File Upload Zone**
- Large drag-drop area for easy interaction
- Clear visual feedback during drag
- Success/error states match Eightfold colors
- Gradient border on hover suggests AI processing

**Field Mapping Interface**
- Teal highlights for matched fields
- Navy text for clear readability
- Connection lines use gradient for visual interest
- Confidence badges use Eightfold color scale

**Data Preview Tables**
- Clean, minimal design focuses on data
- Hover states help track across columns
- Sticky headers for long datasets
- Responsive collapsing on mobile

**Progress Indicators**
- Gradient fills suggest AI working
- Smooth animations reduce perceived wait time
- Clear percentage/step indicators
- Matches overall brand aesthetic

---

## Quick Reference

### Most Common Patterns

**Primary CTA Button**
```html
<button class="px-10 py-3 bg-eightfold-teal text-eightfold-navy font-semibold rounded-pill hover:-translate-y-0.5 transition-all duration-300">
  Get Started
</button>
```

**Standard Card**
```html
<div class="bg-white dark:bg-gray-800/50 rounded-xl p-8 shadow-card border border-gray-200 dark:border-gray-700">
  <!-- Content -->
</div>
```

**Section Header**
```html
<h2 class="text-h2 font-bold text-eightfold-navy dark:text-white mb-4">
  Section Title
</h2>
```

**Input Field**
```html
<input
  type="text"
  class="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-eightfold-teal focus:ring-3 focus:ring-eightfold-teal/20 transition-all"
  placeholder="Enter value"
/>
```

**Badge**
```html
<span class="inline-flex items-center px-4 py-1.5 text-xs font-semibold uppercase tracking-wide rounded-pill bg-eightfold-teal/20 text-eightfold-teal border border-eightfold-teal">
  AI Powered
</span>
```

---

## Appendix

### Brand Assets

**Logo Usage**
- Use Eightfold logo in header/footer if licensed
- Maintain clear space around logo (minimum: logo height)
- Dark version on light backgrounds, light version on dark
- Never distort, rotate, or recolor

**Iconography**
- Use lucide-react icon library (similar to Eightfold style)
- 24px default size, scale proportionally
- Use teal color for primary icons
- Match icon weight to surrounding text

### Accessibility Checklist

- [ ] Color contrast ratios meet WCAG AA (4.5:1 for text)
- [ ] All interactive elements have focus indicators
- [ ] Touch targets minimum 44x44px
- [ ] Form labels properly associated
- [ ] Alt text for all images
- [ ] Keyboard navigation works for all functions
- [ ] Screen reader testing completed
- [ ] Motion respects prefers-reduced-motion
- [ ] Semantic HTML used throughout
- [ ] ARIA labels where needed

### Browser Support

**Target Support:**
- Chrome/Edge: last 2 versions
- Firefox: last 2 versions
- Safari: last 2 versions
- Mobile Safari: iOS 13+
- Chrome Android: last 2 versions

**Graceful Degradation:**
- backdrop-filter fallbacks for older browsers
- CSS Grid with flexbox fallback
- Gradient fallbacks to solid colors
- Custom properties with standard CSS fallbacks

### Performance Considerations

**Font Loading**
- Use font-display: swap for FOUT prevention
- Preload critical font weights
- Subset fonts if possible

**Image Optimization**
- WebP with JPEG/PNG fallbacks
- Responsive images with srcset
- Lazy loading for below-fold images

**CSS Optimization**
- Purge unused Tailwind classes
- Minify production CSS
- Critical CSS inlined
- Non-critical CSS deferred

---

## Conclusion

This design system transforms SnapMap into an authentic Eightfold product while maintaining its core functionality. The vibrant teal and navy palette, combined with Gilroy typography and generous spacing, creates a modern, professional interface that feels both innovative and trustworthy.

Key takeaways:
1. Teal is the hero color - use it prominently for CTAs and accents
2. Gradients add sophistication - apply judiciously to heroes and features
3. Pill-shaped buttons (112px radius) are signature Eightfold
4. 12px card radius and 32px padding create premium feel
5. Fluid typography scales beautifully across devices
6. Dark mode is first-class, not an afterthought

By following this guide, SnapMap will seamlessly integrate into the Eightfold.ai product ecosystem while providing an exceptional user experience for HR professionals transforming their data.

---

**Document prepared by:** UI/UX Design Team
**For questions or clarifications:** Refer to component implementation examples and quick reference section
