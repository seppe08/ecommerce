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
   color-scheme: light;

   --bg-page: #F7F8FC;
   --bg-surface: #FFFFFF;
   --bg-surface-elevated: #FFFFFF;
   --bg-subtle: #F1F3F9;
   --bg-input: #FFFFFF;

   --text-primary: #171B2D;
   --text-secondary: #555D73;
   --text-muted: #858DA3;
   --text-inverse: #FFFFFF;

   --primary: #635BDB;
   --primary-hover: #5149C6;
   --primary-active: #433CAB;
   --primary-light: #EFEEFF;
   --primary-focus: rgba(99, 91, 219, 0.22);

   --error: #DC525D;
   --error-bg: #FFF0F1;
   --error-border: #F5C8CC;
   --error-text: #A52F3A;

   --success: #16876A;
   --success-bg: #EAF8F2;
   --success-border: #B8E6D3;
   --success-text: #12664F;

   --warning: #B7791F;
   --warning-bg: #FFF7E8;
   --warning-border: #F2D9A6;
   --warning-text: #875512;

   --info: #287DB5;
   --info-bg: #EDF6FD;
   --info-border: #C4E0F4;
   --info-text: #205D89;

   --border-subtle: #E8EAF1;
   --border-strong: #D6D9E5;
   --border-focus: #8179E8;

   --shadow-sm: 0 1px 2px rgba(23, 27, 45, 0.04);
   --shadow-md: 0 4px 12px rgba(23, 27, 45, 0.05);
   --shadow-lg: 0 10px 28px rgba(23, 27, 45, 0.07);
   --shadow-xl: 0 20px 45px rgba(23, 27, 45, 0.10);

   --radius-sm: 6px;
   --radius-md: 10px;
   --radius-lg: 14px;
   --radius-xl: 20px;
   --radius-full: 9999px;

   --font-sans: Inter, ui-sans-serif, system-ui, sans-serif;

   --text-xs: 0.75rem;
   --text-sm: 0.875rem;
   --text-base: 1rem;
   --text-lg: 1.125rem;
   --text-xl: 1.25rem;
   --text-2xl: 1.5rem;

   --control-height-sm: 2rem;
   --control-height-md: 2.5rem;
   --control-height-lg: 3rem;


   --focus-ring: 0 0 0 3px var(--primary-focus);

   --transition-fast: 150ms ease;
   --transition-normal: 220ms ease;
   }

   [data-theme="dark"],
   .dark {
   color-scheme: dark;

   --bg-page: #0C0F1A;
   --bg-surface: #131827;
   --bg-surface-elevated: #1B2235;
   --bg-subtle: #222A3F;
   --bg-input: #101525;

   --text-primary: #F1F3FA;
   --text-secondary: #B0B8CC;
   --text-muted: #828DA7;
   --text-inverse: #111526;

   --primary: #8B83F6;
   --primary-hover: #A49DFF;
   --primary-active: #756CE5;
   --primary-light: rgba(139, 131, 246, 0.13);
   --primary-focus: rgba(139, 131, 246, 0.30);

   --error: #F17C86;
   --error-bg: rgba(220, 82, 93, 0.12);
   --error-border: rgba(241, 124, 134, 0.25);
   --error-text: #FFB4BA;

   --success: #4BC9A0;
   --success-bg: rgba(22, 135, 106, 0.13);
   --success-border: rgba(75, 201, 160, 0.25);
   --success-text: #8AE5C4;

   --warning: #F0BB61;
   --warning-bg: rgba(183, 121, 31, 0.13);
   --warning-border: rgba(240, 187, 97, 0.25);
   --warning-text: #F8D795;

   --info: #69B8E8;
   --info-bg: rgba(40, 125, 181, 0.13);
   --info-border: rgba(105, 184, 232, 0.25);
   --info-text: #A3D9F6;

   --border-subtle: #252D40;
   --border-strong: #364159;
   --border-focus: #A49DFF;

   --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.25);
   --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.30);
   --shadow-lg: 0 10px 28px rgba(0, 0, 0, 0.35);
   --shadow-xl: 0 20px 45px rgba(0, 0, 0, 0.45);
   }
   
   *,
   *::before,
   *::after {
   box-sizing: border-box;
   }

   html {
   font-family: var(--font-sans);
   font-size: 16px;
   scroll-behavior: smooth;
   }

   body {
   margin: 0;
   background-color: var(--bg-page);
   color: var(--text-primary);
   transition:
      background-color var(--transition-normal),
      color var(--transition-normal);
   }

   button,
   input,
   textarea,
   select {
   font: inherit;
   }

   button {
   cursor: pointer;
   }

   :focus-visible {
   outline: none;
   box-shadow: var(--focus-ring);
   }

   ::selection {
   background: var(--primary-light);
   color: var(--text-primary);
   }

   @media (prefers-reduced-motion: reduce) {
   *,
   *::before,
   *::after {
      scroll-behavior: auto !important;
      transition-duration: 0.01ms !important;
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
   }
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
