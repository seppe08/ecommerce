# Changelog

All notable changes to the **AuraStore** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Changed
- **UI/UX Redesign — Calm, Editorial, Product-First Storefront (Phases 1, 2 & 3):**
  - **Calm Neutral-First Color Palette:** Redesigned light theme to warm off-white (`#FAF9F6`), crisp white surfaces (`#FFFFFF`), neutral text (`#16181D`), and single deep teal accent (`#2B5B5F`, hover `#224A4D`). Redesigned dark theme to warm charcoal (`#0F1012`), elevated surfaces (`#16181C`, `#1D2025`), and muted amber accent (`#D8A65A`). Removed loud violet gradients from buttons and branding.
  - **Fluid Typography Hierarchy:** Integrated Google Fonts `Fraunces` editorial serif for display and section headings alongside `Plus Jakarta Sans` for body/UI controls with fluid `clamp()` type scaling. Added tabular numerals for price display and 65ch max-line-length constraints.
  - **Global Header & Navigation:** Introduced slimmer header with hairline scroll border, responsive search bar (inline desktop, expandable mobile overlay), theme toggle with 44×44px touch target, shopping cart count bump animation, and clean typography.
  - **Multi-Column Application Footer:** Replaced single-line copyright with a 4-column responsive footer (Brand mission, Collections, Customer Care, Member Accounts).
  - **Editorial Home Page:** Replaced startup-style cards with a calm editorial hero, curated "Featured Objects" grid with 4:5 image ratio, secondary gallery image hover crossfade, and AJAX quick-add button, followed by category tiles with real images and zero fabricated reviews.
  - **Product Catalog Showcase (Phase 2):** Overhauled `product_list.html` with breadcrumb navigation, search/sort toolbar, horizontally scrollable category chips with scroll-snap on mobile, responsive 4:5 image grid (2 col mobile, 3 col tablet, 4 col desktop), secondary image hover crossfade, quick-add buttons, and styled zero-result empty state.
  - **Product Detail Experience (Phase 2):** Overhauled `product_detail.html` with desktop sticky gallery, pure CSS click-to-zoom (`scale(1.6)` with smooth transition, no CDN library), interactive thumbnail switcher, sticky buy box with quantity stepper, single dominant CTA, reassuring microcopy, accessible 3-tab specifications panel, and related products rail.
  - **Shopping Cart & Checkout Flow (Phase 3):** Enhanced `cart_detail.html` and `order_create.html` with a clear 3-step progress stepper (`Cart → Checkout → Confirmation`), responsive 2-column layout with sticky summary on desktop, and a mobile-collapsible order summary with smooth toggle on screens ≤ 960px.
  - **Customer Portal & Printable Invoices (Phase 3):** Refined `order_list.html`, `order_created.html`, and `order_detail.html` with calm editorial headers, status badges, and an updated print stylesheet (`@media print`) rendering clean `#000000` text with zero background fills and hidden chrome.
  - **Authentication & Account Views (Phase 3):** Refined `login.html`, `register.html`, `profile.html`, and all four password reset step templates (`password_reset_form.html`, `password_reset_done.html`, `password_reset_confirm.html`, `password_reset_complete.html`). Fully eliminated all inline `style="..."` attributes across all templates in the repository, replacing them with semantic CSS classes while strictly preserving all test assertions and element IDs.
  - **Design System Clean-up:** Added `.u-sr-only` definition, eliminated hard-coded hex colors in dropdowns using tokenized SVGs, deduplicated `.form-grid-2`, and defined missing utility classes (`btn-lg`, `btn-outline`, `badge-primary`, `badge-error`, `text-primary`, `text-success`, `form-helper`, `optional-mark`, `invoice-actions`, `badge-info`, `auth-callout-box`, `status-icon-centered`, `summary-mobile-toggle`).
  - **High-Contrast Dark & Light Mode Harmonization:** Resolved critical legibility bugs across authentication pages and UI controls. Eliminated invisible text in `.auth-showcase` by replacing undefined gradients and inverted text tokens with explicit high-contrast palettes (Deep Teal with crisp white text in Light mode; elevated charcoal `#1D2025` with `#F2F0EB` text and muted amber `#D8A65A` in Dark mode). Added universal button resets eliminating default browser `buttonface` borders on `.password-toggle-btn` and header toggles. Enforced desktop hiding of mobile search toggle. Defined missing `--font-display`, `--primary-contrast`, and `--primary-gradient` design tokens across `:root` and dark theme. Upgraded `.form-label` contrast across all forms.

### Added
- **GitOps Automation & Pre-commit Hooks:**
  - Added `.pre-commit-config.yaml` configured with Astral Ruff (lint and format), `check-yaml`, `end-of-file-fixer`, `trailing-whitespace`, `check-merge-conflict`, and `detect-private-key`.
- **CI/CD GitHub Actions Workflows:**
  - Added `.github/workflows/ci.yml`: Multi-step continuous integration testing pipeline running Ruff linting, formatting check, Django test suite on Python 3.12 with `uv` caching, and deployment security check (`manage.py check --deploy`).
  - Added `.github/workflows/security.yml`: Automated security audit workflow running `pip-audit` for dependency vulnerability scanning and TruffleHog for secret scanning.
- **Developer Workflow & Templates:**
  - Added `.github/PULL_REQUEST_TEMPLATE.md` with comprehensive pre-merge checklist, change summary, and verification evidence sections.
  - Added `.github/ISSUE_TEMPLATE/feature_request.md` for structured feature proposals and design system alignment.
  - Added `.github/ISSUE_TEMPLATE/bug_report.md` for reproducible defect reporting across environments.
- **Contribution & Git Guidelines:**
  - Added `CONTRIBUTING.md` outlining the Conventional Commits standard (`feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `perf:`, `test:`, `chore:`), Git branch naming (`feature/*`, `fix/*`, `chore/*`), local setup with `uv`, pre-commit verification, and PR review workflow.
- **Security Hardening (In Progress):**
  - Production-ready security headers (HSTS, SSL redirect, secure session and CSRF cookies, X-Frame-Options, Content-Security-Policy).
  - Profile avatar upload sanitization, format verification with PIL, and 5MB size limit.

### Fixed
- **CI Linting Compatibility:**
  - Removed redundant `#!/usr/bin/env python` shebang line from `manage.py` resolving Ruff `EXE001` (shebang on non-executable file) failure on Unix-based GitHub Actions runners.

### Planned
- Shopping Cart with persistent session storage and line item management.
- Multi-step checkout pipeline with address capture and order placement.
- Stripe payment gateway integration with webhook event handling.

---

## [0.2.0] - 2026-11-21

### Milestone: Product Catalog & Categories

### Added
- **Catalog Data Models:**
  - `Category` model with unique slug, description, image, and active toggle.
  - `Product` model with pricing, stock counter, SKU uniqueness, indexed slugs, and category foreign key.
  - `ProductImage` model supporting multi-image galleries with designated primary image and fallback logic.
  - Dynamic inventory stock evaluation property `Product.is_in_stock`.
- **Views & User Experience:**
  - Product catalog list view (`/products/`) with dual category filtering (URL slug & query param), full-text search across title, description, and SKU, sorting (price asc/desc, newest, name A-Z), active category chips, and pagination (12 items/page).
  - Product detail showcase (`/products/<slug>/`) featuring interactive thumbnail switcher, stock status badges, specifications table, quantity selector, and related products grid.
- **Django Admin Customization:**
  - `CategoryAdmin` with dynamically annotated product counts, active status filters, and slug auto-population.
  - `ProductAdmin` with tabular `ProductImageInline`, search by SKU/name, and list-editable price/stock fields.
- **Accessibility & Design:**
  - Strict compliance with `DESIGN_SYSTEM.md` and WCAG 2.1 AA standards (minimum 44×44px touch targets, `:focus-visible` rings, semantic markup).
- **Automated Test Coverage:**
  - Comprehensive 23-case test suite in `apps/catalog/tests.py` testing model constraints, stock properties, admin configurations, search, filtering, sorting, pagination, and detail views.

---

## [0.1.0] - 2026-11-20

### Milestone: Authentication & Design System

### Added
- **Core Architecture & Tooling:**
  - Modern Python 3.12+ and Django 6.1+ foundation with Astral `uv` package management and PostgreSQL 18 compatibility via Docker Compose.
  - Twelve-factor environment configuration using `django-environ`.
- **Custom User Model & Authentication:**
  - `apps.accounts.models.CustomUser` extending `AbstractUser` with unique email requirement and profile fields (`phone`, `birth_date`, `profile_picture`).
  - Dual-identifier authentication backend (`EmailOrUsernameModelBackend`) supporting interchangeable, case-insensitive login with username or email, hardened with timing attack defense.
  - Custom login form (`CustomLoginForm`) with empathetic error handling and 30-day "Remember Me" session persistence.
  - Full user registration flow (`RegisterView`, `CustomRegistrationForm`) with password confirmation and automatic post-registration login.
  - User profile management dashboard (`ProfileView`, `UserProfileForm`) for updating personal info and uploading avatars.
  - 4-step secure password reset and recovery workflow using email tokens (`CustomPasswordResetView`, `CustomPasswordResetConfirmView`).
  - Custom logout view with clean session termination and CSRF protection.
- **Design System & Frontend Architecture:**
  - Zero-FOUC Dark and Light theme engine implemented with CSS variables and synchronous theme resolution in `<head>`.
  - Accessible UI components with WCAG 2.1 AA minimum 44×44px touch targets and high-empathy inline error feedback.
- **Automated Test Coverage:**
  - Comprehensive 30-case test suite in `apps/accounts/tests.py` verifying all authentication, registration, profile, password reset, and backend flows.
