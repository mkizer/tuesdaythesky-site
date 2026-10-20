# Color Palette: Obsidian & Crimson Theme

The color palette for **Tuesday The Sky** is derived from the **_Indoor Enthusiast_** album artwork (`src/assets/images/IndoorEnthusiast_cover.png`).

---

## 1. Palette Overview

| Element              | Light Mode             | Dark Mode                    | Rationale                                                |
| :------------------- | :--------------------- | :--------------------------- | :------------------------------------------------------- |
| **Primary Accent**   | `#d62a26` (Crimson)    | `#d62a26` (Vibrant Crimson)  | Matches the bold red title typography of the cover.      |
| **Secondary Accent** | `#b82420` (Deep Ruby)  | `#b82420` (Ruby)             | Button hover states and interactive depth.               |
| **Accent Highlight** | `#e04844` (Coral Red)  | `#e04844` (Vivid Coral)      | Focused highlights and micro-interactions.               |
| **Page Background**  | `#f5f6f8` (Ice Silver) | `#111215` (Obsidian / Slate) | Cool marble tones from the artwork frame and deep space. |
| **Headings**         | `#0f1115`              | `#f3f4f6`                    | Clean, high-contrast, modern typography.                 |
| **Default Text**     | `#1e2024`              | `#e2e5ea`                    | Optimal readability across viewports.                    |
| **Muted Text**       | `rgb(30 32 36 / 66%)`  | `rgb(226 229 234 / 66%)`     | Subdued secondary info and timestamps.                   |

---

## 2. Slate Color Scale (Cool Steel / Obsidian)

Tailwind CSS v4 theme tokens mapped in `src/assets/styles/tailwind.css`:

```css
--color-slate-50: #f8fafc;
--color-slate-100: #f1f4f8;
--color-slate-200: #e2e7ee;
--color-slate-300: #cbd4e0;
--color-slate-400: #94a0b2;
--color-slate-500: #647287;
--color-slate-600: #434c5c;
--color-slate-700: #2d3440;
--color-slate-800: #1c2028;
--color-slate-900: #12151b;
--color-slate-950: #0b0d11;
```

---

## 3. Implementation Files

- **Global CSS Variables**: [CustomStyles.astro](file:///c:/Users/Michael/Projects/tuesdaythesky-site/src/components/CustomStyles.astro)
- **Tailwind v4 Theme**: [tailwind.css](file:///c:/Users/Michael/Projects/tuesdaythesky-site/src/assets/styles/tailwind.css)
