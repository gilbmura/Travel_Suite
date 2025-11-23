# Travel Suite Design Guide

## Color Palette (African-Inspired)

The design uses a warm, bold color palette inspired by African aesthetics:

### Primary Colors
- **Deep Orange**: `#E67E22` - Primary action color, warmth, energy
- **Gold**: `#F39C12` - Accent color, premium feel, highlights
- **Forest Green**: `#27AE60` - Success states, nature, growth
- **Dark Slate**: `#2C3E50` - Text, headers, depth

### Neutral Colors
- **Warm White**: `#FDF6E3` - Background, light sections
- **Warm Gray**: `#ECF0F1` - Secondary backgrounds
- **Medium Gray**: `#95A5A6` - Secondary text
- **Dark Gray**: `#34495E` - Body text

### CSS Variables

```css
:root {
  --color-primary: #E67E22;
  --color-primary-dark: #D35400;
  --color-gold: #F39C12;
  --color-green: #27AE60;
  --color-slate: #2C3E50;
  --color-white: #FDF6E3;
  --color-gray-light: #ECF0F1;
  --color-gray: #95A5A6;
  --color-gray-dark: #34495E;
  --color-text: #2C3E50;
  --color-text-light: #7F8C8D;
  --color-border: #BDC3C7;
  --color-success: #27AE60;
  --color-error: #E74C3C;
  --color-warning: #F39C12;
}
```

## Typography

- **Headings**: Bold, large, readable
  - H1: 2.5rem (40px), font-weight: 700
  - H2: 2rem (32px), font-weight: 700
  - H3: 1.5rem (24px), font-weight: 600
  
- **Body**: Clean, readable
  - Base: 1rem (16px), font-weight: 400
  - Line height: 1.6 for readability

- **Font Family**: System fonts stack for performance
  ```css
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  ```

## Layout Principles

1. **Mobile-First**: Design for mobile, enhance for desktop
2. **Generous White Space**: Use padding and margins liberally
3. **Rounded Corners**: Cards and buttons use `border-radius: 8px` or `12px`
4. **Elevation**: Subtle shadows for depth (`box-shadow: 0 2px 8px rgba(0,0,0,0.1)`)
5. **Clear CTAs**: Primary actions are prominent and clearly visible

## Component Styles

### Buttons
- Primary: Deep orange background, white text, rounded
- Secondary: Transparent with border, slate text
- Hover: Slight darkening, smooth transition

### Cards
- White background, rounded corners, subtle shadow
- Padding: 1.5rem
- Border: 1px solid light gray (optional)

### Forms
- Inputs: Rounded, border, focus state with primary color
- Labels: Bold, clear
- Error states: Red border, error message below

## CSS Utility Classes

```css
/* Spacing */
.mt-1 { margin-top: 0.5rem; }
.mt-2 { margin-top: 1rem; }
.mt-3 { margin-top: 1.5rem; }
.mb-1 { margin-bottom: 0.5rem; }
.mb-2 { margin-bottom: 1rem; }
.p-1 { padding: 0.5rem; }
.p-2 { padding: 1rem; }
.p-3 { padding: 1.5rem; }

/* Text */
.text-center { text-align: center; }
.text-bold { font-weight: 700; }
.text-primary { color: var(--color-primary); }

/* Layout */
.container { max-width: 1200px; margin: 0 auto; padding: 0 1rem; }
.flex { display: flex; }
.flex-column { flex-direction: column; }
.flex-center { justify-content: center; align-items: center; }
.grid { display: grid; gap: 1rem; }

/* Buttons */
.btn { padding: 0.75rem 1.5rem; border-radius: 8px; border: none; cursor: pointer; transition: all 0.3s; }
.btn-primary { background: var(--color-primary); color: white; }
.btn-primary:hover { background: var(--color-primary-dark); }
.btn-secondary { background: transparent; border: 2px solid var(--color-primary); color: var(--color-primary); }
```

## Pattern Watermark

A subtle traditional pattern can be used as a watermark on hero sections or ticket backgrounds. In MVP, this is implemented as a very light background pattern or omitted for simplicity.

## Accessibility

- Minimum contrast ratio: 4.5:1 for text
- Focus states clearly visible
- Touch targets minimum 44x44px
- Semantic HTML structure

