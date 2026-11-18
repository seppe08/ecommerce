# Design System & UI/UX Constitution

> **Status:** Active & Mandatory  
> **Target:** Entire E-Commerce Platform & Django Application Ecosystem  
> **Rule of Thumb:** Every template, view, component, and interaction in this project MUST comply with the rules set in this document. Never compromise on accessibility, responsiveness, typographic hierarchy, or theme consistency.

---

## 1. Core Visual Principles & Non-Negotiables

These are the strict principles that must never be compromised:

1. **Zero Flash of Unstyled Content / Theme Flash (FOUC):**
   - The user's theme preference (`light` or `dark`) must be resolved **synchronously** in the `<head>` of the document before DOM rendering begins.
   - Persist theme selection in `localStorage` with a fallback to `window.matchMedia('(prefers-color-scheme: dark)')`.

2. **Perfect Error Handling & High-Empathy Feedback:**
   - Never show raw Django unstyled error lists or browser-native alert popups.
   - Field-specific errors must be anchored **directly beneath** the offending input with an alert icon, clear contrast, and helpful remediation guidance.
   - Form-level non-field errors must be displayed in an accessible banner alert at the top of the card/page.
   - Form inputs with errors must visually reflect the error state with a crimson border, focus glow, and `aria-invalid="true"`.

3. **Accessibility First (WCAG 2.1 AA Compliant):**
   - All interactive controls (buttons, inputs, links) must meet minimum touch targets of at least **44×44px**.
   - Contrast ratios must exceed 4.5:1 for normal text and 3:1 for large headings.
   - All interactive elements must exhibit visible, glowing focus rings (`:focus-visible`) for keyboard navigation.
   - Every icon button (e.g., password toggle, theme switcher, close alert) must have a descriptive `aria-label`.

4. **Tactile Micro-Interactions & Perceived Performance:**
   - Buttons, inputs, and cards must feel alive with smooth 150ms–200ms cubic transitions (`transform`, `background-color`, `border-color`, `box-shadow`).
   - Action buttons must provide instant feedback: hover elevation, active press-down (`scale(0.99)`), and loading spinner state upon form submission to prevent duplicate clicks.

---

## 2. Color Palette & Theme Tokens

All colors are exposed through CSS custom properties on `:root` and `[data-theme="dark"]` / `.dark`.

### Color Token Architecture

```css
:root {
  /* Surface & Background */
  --bg-page: #f8fafc;            /* Slate 50 */
  --bg-surface: #ffffff;         /* Pure White */
  --bg-surface-elevated: #ffffff;/* Cards, modals */
  --bg-subtle: #f1f5f9;          /* Slate 100 */
  --bg-input: #ffffff;

  /* Typography */
  --text-primary: #0f172a;       /* Slate 900 - high contrast */
  --text-secondary: #475569;     /* Slate 600 - supporting info */
  --text-muted: #64748b;         /* Slate 500 - helper copy */
  --text-inverse: #ffffff;

  /* Brand Accents (Modern Indigo / Violet Luxury) */
  --primary: #4f46e5;            /* Indigo 600 */
  --primary-hover: #4338ca;      /* Indigo 700 */
  --primary-light: #eef2ff;      /* Indigo 50 */
  --primary-focus: rgba(79, 70, 229, 0.25);

  /* Semantic Feedback */
  --error: #ef4444;              /* Rose 500 */
  --error-bg: #fef2f2;           /* Rose 50 */
  --error-border: #fecaca;       /* Rose 200 */
  --error-text: #991b1b;         /* Rose 800 */

  --success: #10b981;            /* Emerald 500 */
  --success-bg: #ecfdf5;         /* Emerald 50 */
  --success-border: #a7f3d0;     /* Emerald 200 */
  --success-text: #065f46;       /* Emerald 800 */

  --warning: #f59e0b;            /* Amber 500 */
  --warning-bg: #fffbeb;         /* Amber 50 */
  --warning-border: #fde68a;     /* Amber 200 */
  --warning-text: #92400e;       /* Amber 800 */

  --info: #0ea5e9;               /* Sky 500 */
  --info-bg: #f0f9ff;            /* Sky 50 */
  --info-border: #bae6fd;        /* Sky 200 */
  --info-text: #075985;          /* Sky 800 */

  /* Borders & Dividers */
  --border-subtle: #e2e8f0;      /* Slate 200 */
  --border-strong: #cbd5e1;      /* Slate 300 */
  --border-focus: #6366f1;       /* Indigo 500 */

  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(15, 23, 42, 0.08), 0 2px 4px -2px rgba(15, 23, 42, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(15, 23, 42, 0.08), 0 4px 6px -4px rgba(15, 23, 42, 0.05);
  --shadow-xl: 0 20px 25px -5px rgba(15, 23, 42, 0.10), 0 8px 10px -6px rgba(15, 23, 42, 0.05);

  /* Radius */
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 14px;
  --radius-full: 9999px;
}

[data-theme="dark"] {
  /* Surface & Background (Deep obsidian / slate, never washed-out gray) */
  --bg-page: #0b0f19;            /* Pitch Slate */
  --bg-surface: #111827;         /* Gray 900 */
  --bg-surface-elevated: #1e293b;/* Slate 800 */
  --bg-subtle: #1e293b;          /* Slate 800 */
  --bg-input: #0f172a;           /* Deep input slot */

  /* Typography */
  --text-primary: #f8fafc;       /* Slate 50 */
  --text-secondary: #cbd5e1;     /* Slate 300 */
  --text-muted: #94a3b8;         /* Slate 400 */
  --text-inverse: #0f172a;

  /* Brand Accents */
  --primary: #6366f1;            /* Indigo 500 - brighter for dark mode */
  --primary-hover: #818cf8;      /* Indigo 400 */
  --primary-light: rgba(99, 102, 241, 0.15);
  --primary-focus: rgba(99, 102, 241, 0.35);

  /* Semantic Feedback */
  --error: #f87171;              /* Rose 400 */
  --error-bg: rgba(239, 68, 68, 0.12);
  --error-border: rgba(239, 68, 68, 0.3);
  --error-text: #fca5a5;

  --success: #34d399;            /* Emerald 400 */
  --success-bg: rgba(16, 185, 129, 0.12);
  --success-border: rgba(16, 185, 129, 0.3);
  --success-text: #6ee7b7;

  --warning: #fbbf24;            /* Amber 400 */
  --warning-bg: rgba(245, 158, 11, 0.12);
  --warning-border: rgba(245, 158, 11, 0.3);
  --warning-text: #fde68a;

  --info: #38bdf8;               /* Sky 400 */
  --info-bg: rgba(14, 165, 233, 0.12);
  --info-border: rgba(14, 165, 233, 0.3);
  --info-text: #7dd3fc;

  /* Borders & Dividers */
  --border-subtle: #1e293b;      /* Slate 800 */
  --border-strong: #334155;      /* Slate 700 */
  --border-focus: #818cf8;

  /* Shadows (Tuned for dark backgrounds) */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.4);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.5), 0 2px 4px -2px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.6), 0 4px 6px -4px rgba(0, 0, 0, 0.5);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.7), 0 8px 10px -6px rgba(0, 0, 0, 0.6);
}
```

---

## 3. Typography System & Hierarchy

- **Font Family:**  
  `font-family: 'Plus Jakarta Sans', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;`  
  Selected for exceptional legibility on high-DPI and standard screens, modern geometric curves, and distinct letterforms.

| Scale Token | Font Size | Line Height | Weight | Letter Spacing | Purpose / Role |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `display-1` | 2.25rem (36px) | 1.15 | 800 | -0.025em | Main hero headlines, splash headers |
| `heading-1` | 1.75rem (28px) | 1.25 | 700 | -0.02em | Card / Form title, Page H1 |
| `heading-2` | 1.375rem (22px) | 1.3 | 600 | -0.015em | Section header, modal title |
| `subheading`| 1.0625rem (17px)| 1.4 | 500 | 0 | Descriptive taglines below titles |
| `body-normal`| 0.9375rem (15px)| 1.55 | 400 / 500 | 0 | Standard body copy, inputs |
| `label-bold`| 0.875rem (14px) | 1.25 | 600 | -0.01em | Form labels, navigation tabs |
| `helper-text`| 0.8125rem (13px)| 1.4 | 500 | 0 | Validation errors, input hints |
| `micro-badge`| 0.75rem (12px)  | 1 | 700 | 0.04em uppercase | Status tags, pill badges |

---

## 4. Form UX & Input Component Standards

### Input Anatomy
1. **Label (`<label>`):**
   - Must have `for="<input-id>"`.
   - Clear weight (`600`), readable color (`var(--text-secondary)`), subtle bottom margin (`6px`).
   - Required fields marked with clean semantic indicators.
2. **Input Wrapper:**
   - Positioned relative to support leading/trailing icon slots.
3. **Leading Icon Slot:**
   - 18–20px SVG icon in `var(--text-muted)` to communicate field intent (e.g., Mail, Lock, User).
4. **Input Control (`<input>`):**
   - Height: min `46px` for effortless click/tap.
   - Border: `1.5px solid var(--border-subtle)`.
   - Padding: Left padded (`42px`) when icon is present; right padded (`44px`) when action icon (like eye toggle) is present.
   - Transition: `border-color 0.2s ease, box-shadow 0.2s ease`.
   - Focus State: Border switches to `var(--border-focus)`, box-shadow glows with `0 0 0 3px var(--primary-focus)`.
5. **Interactive Trailing Slot (e.g., Password Visibility Toggle):**
   - Clickable button (`type="button"`) with `aria-label="Toggle password visibility"`.
   - Eye / Eye-off icon transitioning without disturbing the password value.
6. **Inline Validation Message:**
   - Placed immediately below the input.
   - Includes alert icon, font-size `0.8125rem`, color `var(--error)`.
   - Connected via `aria-describedby` when errors occur.

---

## 5. Theme Switcher Component Specifications

- Floating or top-header toggle button with smooth circular shape.
- Visual icon indicates target mode or current status (Sun for light, Moon for dark).
- Accessible keyboard activation via `Enter` or `Space`.
- Seamless JavaScript snippet executing immediately in `<head>` to read saved theme from `localStorage` or fallback to system preference.

---

## 6. Verification Checklist Before Any Feature Sign-Off

- [ ] Does it render flawlessly in **both Light and Dark modes**?
- [ ] Is there zero flash of wrong theme upon page load/refresh?
- [ ] Do all colors meet accessible contrast requirements?
- [ ] Are form error states crystal clear with explicit remediation hints?
- [ ] Is every input keyboard accessible with a distinct `:focus-visible` ring?
- [ ] Are font sizes and weights aligned with the Typography Scale?
- [ ] Are buttons equipped with hover, active, and loading states?
- [ ] Is the layout fully responsive from 320px mobile screens to desktop?

---

*This document is the single source of truth for UI/UX standards in this repository.*
