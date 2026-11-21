# Design System & UI/UX Constitution

> **Status:** Active & Mandatory  
> **Target:** Entire AuraStore E-Commerce Platform & Django Application Ecosystem  
> **Rule of Thumb:** Every template, view, component, and interaction in this project MUST comply with the rules set in this document. Never compromise on accessibility, responsiveness, typographic hierarchy, or theme consistency. AuraStore adheres to a calm, editorial, product-first retail aesthetic.

---

## 1. Core Visual Principles & Non-Negotiables

These are the strict principles that must never be compromised:

1. **Zero Flash of Unstyled Content / Theme Flash (FOUC):**
   - The user's theme preference (`light` or `dark`) must be resolved **synchronously** in the `<head>` of the document before DOM rendering begins.
   - Persist theme selection in `localStorage` with a fallback to `window.matchMedia('(prefers-color-scheme: dark)')`.
   - Theme toggle transitions smoothly via CSS cross-fade without full-page flashing.

2. **Neutral-First, Product-First Visual Chrome:**
   - UI chrome is calm, restrained, and editorial. Color comes from high-quality product photography, not loud gradient buttons or neon accents.
   - Single accent per theme: deep teal (`#2B5B5F`) for Light mode; muted amber (`#D8A65A`) for Dark mode.
   - Solid buttons with subtle hover shifts instead of violet gradients or glowing shadows.

3. **Accessibility First (WCAG 2.1 AA Compliant):**
   - All interactive controls (buttons, inputs, links, toggles) meet minimum touch targets of at least **44×44px**.
   - Contrast ratios exceed 4.5:1 for normal text (e.g., `#5C6270` on `#FFFFFF` is 5.7:1) and 3:1 for large headings.
   - All interactive elements exhibit visible, dedicated focus rings (`:focus-visible`) for keyboard navigation.
   - Every icon button has an accessible `aria-label`.

4. **Tactile Micro-Interactions & Reduced-Motion Respect:**
   - Buttons, inputs, and cards react with smooth 150ms–220ms transitions (`transform`, `background-color`, `border-color`, `box-shadow`).
   - Action buttons provide tactile press feedback (`scale(0.98)`).
   - `@media (prefers-reduced-motion: reduce)` disables scale transforms and keeps only subtle opacity changes.

---

## 2. Color Palette & Theme Tokens

All colors are exposed through CSS custom properties on `:root` and `[data-theme="dark"]` / `.dark`.

### Color Token Architecture

```css
:root {
  color-scheme: light;

  /* Surfaces - Warm off-white page, crisp white surfaces */
  --bg-page: #FAF9F6;
  --bg-surface: #FFFFFF;
  --bg-surface-elevated: #FFFFFF;
  --bg-subtle: #F2EFE9;
  --bg-input: #FFFFFF;
  --bg-input-focus: #FFFFFF;

  /* Typography - Neutral, high contrast */
  --text-primary: #16181D;
  --text-secondary: #5C6270;
  --text-muted: #888F9E;
  --text-inverse: #FFFFFF;

  /* Brand Accent - Single deep teal accent for Light mode */
  --primary: #2B5B5F;
  --primary-hover: #224A4D;
  --primary-active: #1A393C;
  --primary-light: rgba(43, 91, 95, 0.08);
  --primary-focus: rgba(43, 91, 95, 0.22);
  --btn-primary-text: #FFFFFF;
  --primary-contrast: #FFFFFF;
  --primary-gradient: linear-gradient(145deg, #1A3E42 0%, #2B5B5F 100%);

  /* Desaturated Semantics */
  --error: #A83A3A;
  --error-bg: #FAEEEE;
  --error-border: #ECCECE;
  --error-text: #822626;

  --success: #2E6B56;
  --success-bg: #EDF5F1;
  --success-border: #C8DFD4;
  --success-text: #1E4E3E;

  --warning: #966320;
  --warning-bg: #FBF4E8;
  --warning-border: #ECD8B6;
  --warning-text: #734812;

  --info: #355C7D;
  --info-bg: #EFF4F8;
  --info-border: #C7D8E6;
  --info-text: #23415A;

  /* Hairlines & Borders */
  --border-subtle: #E7E5E0;
  --border-strong: #D3D0C8;
  --border-focus: #2B5B5F;

  /* Soft, low-contrast shadows */
  --shadow-sm: 0 1px 2px rgba(22, 24, 29, 0.04);
  --shadow-md: 0 4px 12px rgba(22, 24, 29, 0.05);
  --shadow-lg: 0 12px 28px rgba(22, 24, 29, 0.07);
  --shadow-xl: 0 20px 45px rgba(22, 24, 29, 0.10);

  /* Radii */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-full: 9999px;

  /* Fonts */
  --font-serif: 'Fraunces', 'Instrument Serif', Georgia, 'Times New Roman', serif;
  --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-display: var(--font-serif);

  /* Control Heights */
  --control-height-sm: 2.25rem;
  --control-height-md: 2.75rem;
  --control-height-lg: 3rem;

  --focus-ring: 0 0 0 3px var(--primary-focus);
  --focus-ring-error: 0 0 0 3px rgba(168, 58, 58, 0.25);

  --transition-fast: 150ms ease;
  --transition-normal: 220ms ease;
  --transition-slow: 350ms ease;
}

[data-theme="dark"],
.dark {
  color-scheme: dark;

  /* Surfaces - Warm charcoal, not pure black */
  --bg-page: #0F1012;
  --bg-surface: #16181C;
  --bg-surface-elevated: #1D2025;
  --bg-subtle: #23272E;
  --bg-input: #121417;
  --bg-input-focus: #16181C;

  /* Typography */
  --text-primary: #F2F0EB;
  --text-secondary: #A8ADB8;
  --text-muted: #727782;
  --text-inverse: #0F1012;

  /* Brand Accent - Muted amber for Dark mode */
  --primary: #D8A65A;
  --primary-hover: #C59347;
  --primary-active: #B28135;
  --primary-light: rgba(216, 166, 90, 0.12);
  --primary-focus: rgba(216, 166, 90, 0.25);
  --btn-primary-text: #0F1012;
  --primary-contrast: #0F1012;
  --primary-gradient: linear-gradient(145deg, #15171B 0%, #1D2026 100%);

  /* Desaturated Semantics */
  --error: #E06D6D;
  --error-bg: rgba(224, 109, 109, 0.12);
  --error-border: rgba(224, 109, 109, 0.25);
  --error-text: #F0A8A8;

  --success: #52B788;
  --success-bg: rgba(82, 183, 136, 0.12);
  --success-border: rgba(82, 183, 136, 0.25);
  --success-text: #95D5B2;

  --warning: #D8A65A;
  --warning-bg: rgba(216, 166, 90, 0.12);
  --warning-border: rgba(216, 166, 90, 0.25);
  --warning-text: #E8C488;

  --info: #6BA3C7;
  --info-bg: rgba(107, 163, 199, 0.12);
  --info-border: rgba(107, 163, 199, 0.25);
  --info-text: #A8CCE0;

  /* Hairlines & Borders */
  --border-subtle: #262A31;
  --border-strong: #383E49;
  --border-focus: #D8A65A;

  /* Dark elevation shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.35);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.45);
  --shadow-lg: 0 12px 28px rgba(0, 0, 0, 0.55);
  --shadow-xl: 0 20px 45px rgba(0, 0, 0, 0.65);

  --focus-ring-error: 0 0 0 3px rgba(224, 109, 109, 0.30);
}
```

---

## 3. Typography System & Hierarchy

- **Font Stacks:**  
  - Heading / Display: `--font-serif: 'Fraunces', 'Instrument Serif', Georgia, serif;` (refined editorial serif)  
  - Body & Controls: `--font-sans: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;`  

| Scale Token / Selector | Font Size (Fluid clamp) | Line Height | Weight | Letter Spacing | Purpose / Role |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `hero-display` / `.u-display-hero` | `clamp(2.75rem, 5vw + 1rem, 4.5rem)` | 1.05 | 600 / 700 (Serif) | -0.025em | Editorial hero headline |
| `page-h1` / `.u-heading-1` | `clamp(2rem, 3vw + 1rem, 2.75rem)` | 1.15 | 600 / 700 (Serif) | -0.02em | Page title, splash hero |
| `section-h2` / `.u-heading-2` | `clamp(1.5rem, 2vw + 0.75rem, 2rem)` | 1.25 | 600 (Serif) | -0.015em | Section titles, panel headers |
| `card-title` / `.u-heading-3` | `1.0625rem–1.125rem` | 1.4 | 600 (Sans) | -0.01em | Product title, card title |
| `body` / `.u-body` | `1rem` (16px) | 1.6 | 400 (Sans) | 0 | Body copy (max line length 65ch) |
| `meta-label` / `.u-label` | `0.8125rem–0.875rem` | 1.35 | 500 / 600 (Sans) | 0 | Form labels, SKU, secondary meta |
| `eyebrow` / `.u-eyebrow` | `0.75rem` | 1.2 | 700 (Sans) | 0.12em uppercase | Category eyebrow, section kicker |
| `price` / `.product-card-price` | `1.125rem–1.375rem` | 1.2 | 700 (Sans) | `tabular-nums` | Prominent price emphasis |

---

## 4. Product Showcase & Grid Standards

1. **Aspect Ratio & Imagery:**
   - Product media cards strictly utilize `4:5` aspect ratio (`aspect-ratio: 4 / 5`).
   - Image rendering: `object-fit: cover; width: 100%; height: 100%;`.
   - Hover transition: crossfade to second image if present, or subtle `scale(1.03)` zoom.
2. **Responsive Columns:**
   - Mobile (< 640px): 2 columns.
   - Tablet (640px – 1024px): 3 columns.
   - Desktop (> 1024px): 4 columns.
3. **Quick-Add Button:**
   - Hover/focus revealed on desktop; persistent touch control on mobile.
   - Submits existing AJAX `cart_add` endpoint.
4. **Stock Badges:**
   - Restrained to relevant states only: "Low Stock (X left)" or "Out of Stock". No badge clutter for ample stock.

---

## 5. Cart, Checkout & Account Standards

1. **Checkout Stepper Navigation:**
   - 3-step progress indicator: `Cart → Checkout → Confirmation`.
   - Completed steps show checkmarks and link back to editable views; active step highlighted with accent color.
2. **Two-Column Sticky Layout:**
   - Desktop: 2-column layout with sticky order summary (`top: 90px`).
   - Mobile: Single column with collapsible order summary toggle (`.summary-mobile-toggle`) providing clean space and expandable item details.
3. **Printable Invoices:**
   - Print stylesheet (`@media print`) hides all UI chrome (`.no-print`, header, footer, breadcrumbs).
   - Printable sheet renders with pure black text (`#000000`), zero background fills, and clean hairline borders.
4. **Zero Inline Styles:**
   - All components, banners, hints, and error alerts are strictly token-driven via CSS classes. No inline `style="..."` attributes permitted.

---

## 6. Motion Tokens & Interactions

1. **Transitions:**
   - Fast (`150ms ease`): Button color, hover shift, icon transitions.
   - Normal (`220ms ease`): Card hover elevation, border shifts.
   - Slow (`350ms ease`): Image crossfades, menu reveals.
2. **Page Reveals:**
   - Staggered IntersectionObserver reveal with `.reveal-on-scroll` adding `.is-visible`.
3. **Flash Messages:**
   - Slide in from top, auto-dismiss after 5 seconds with pause on user hover/focus.
4. **Cart Bump:**
   - 250ms scale bump animation on header cart count pill whenever quantity changes.
5. **Reduced Motion:**
   - `@media (prefers-reduced-motion: reduce)` removes scale transforms and keeps subtle opacity transitions.

---

## 7. Verification Checklist Before Any Feature Sign-Off

- [ ] Does it render flawlessly in **both Light and Dark modes**?
- [ ] Is there zero flash of wrong theme upon page load/refresh?
- [ ] Do all colors meet accessible contrast requirements (≥ 4.5:1 for normal text)?
- [ ] Are form error states crystal clear with explicit remediation hints?
- [ ] Is every input keyboard accessible with a distinct `:focus-visible` ring?
- [ ] Are font sizes and weights aligned with the Typography Scale?
- [ ] Are buttons equipped with hover, active (`scale(0.98)`), and loading states?
- [ ] Is the layout fully responsive from 320px mobile screens to desktop?

---

*This document is the single source of truth for UI/UX standards in this repository.*
