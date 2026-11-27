# Changelog

All notable changes to the **AuraStore** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- **Stripe & Card Payment Gateway Integration:**
  - Integrated Stripe payment processing alongside Cash on Delivery (COD) checkout selection (`payment_method`, `stripe_payment_intent_id`, `Order.mark_as_paid()`).
  - Added `/orders/payment/<order_number>/` payment portal with sandbox test card support, decline simulation, COD switching, and `/orders/webhook/stripe/` webhook handler.
- **Promotions & Coupon Discount System:**
  - Added `Coupon` model supporting percentage and fixed-amount discounts, validity windows, usage caps, and minimum order spend.
  - Integrated coupon redemption (`/cart/coupon/apply/`, `/cart/coupon/remove/`) into session-backed `Cart` and `Order` records.
- **Customer Product Reviews & Star Ratings:**
  - Added `Review` model (1–5 stars, headline, text, unique per user/product) with automated verified-buyer badges and dynamic `average_rating`, `review_count`, and `rating_distribution` metrics.
- **Customer Wishlist & Saved Items:**
  - Added `Wishlist` model, `/products/wishlist/` portal, and AJAX heart toggle on product cards and detail pages.
- **Saved Customer Address Book:**
  - Added `Address` model in `apps/accounts` with default shipping address auto-fill and 1-click address selector chips during checkout.
- **Order Cancellation & Inventory Replenishment:**
  - Added `/orders/cancel/<order_number>/` endpoint with `transaction.atomic()` and `select_for_update()` stock restoration for pending orders.
- **Transactional Order Confirmation Emails:**
  - Added itemized HTML and plaintext order confirmation emails (`templates/orders/emails/order_confirmation.*`) dispatched via `EmailMultiAlternatives`.
- **Database Seeding Command (`seed_db`):**
  - Added `uv run python manage.py seed_db` management command populating sample categories, products, reviews, coupons (`WELCOME10`, `SAVE20`, `FLAT25`), and a demo customer account.
- **Tailwind CSS v4 Build Pipeline (Option A — Server-Rendered Django Proof of Concept):**
  - Integrated `@tailwindcss/cli` v4 and `tailwindcss` with `package.json` scripts (`build:css` and `watch:css`).
  - Added single source of truth token mapping in `static/css/tailwind/input.css` using `@theme` referencing existing CSS variables (`--color-page`, `--color-surface`, `--color-subtle`, `--color-ink`, `--color-ink-2`, `--color-ink-3`, `--color-line`, `--color-line-strong`, `--color-accent`, `--color-accent-hover`, `--color-accent-fg`, `--color-success*`, `--color-warning*`, `--color-error*`, `--radius-card`, `--radius-control`, `--font-body`, `--font-editorial`).
  - Compiled and committed static bundle `static/css/app.css` to allow zero-Node Python-only deployment pipelines.
  - Created unified, reusable product card template `templates/includes/product_card.html` with 4:5 media aspect ratio, 500ms secondary image hover crossfade, restrained semantic stock badges, desktop hover/focus and touch-persistent quick-add button, clamped description, tabular price, and 44px touch target secondary "View Details" button.
- **GitOps Automation & Pre-commit Hooks:**
  - Added `.pre-commit-config.yaml` configured with Astral Ruff (lint and format), `check-yaml`, `end-of-file-fixer`, `trailing-whitespace`, `check-merge-conflict`, and `detect-private-key`.
- **CI/CD GitHub Actions Workflows:**
  - Added `.github/workflows/ci.yml`: Multi-step continuous integration testing pipeline running Ruff linting, formatting check, Django test suite on Python 3.12 with `uv` caching, and deployment security check (`manage.py check --deploy`).
  - Added `.github/workflows/security.yml`: Automated security audit workflow running `pip-audit` for dependency vulnerability scanning and TruffleHog for secret scanning.
- **Developer Workflow & Templates:**
  - Added `.github/PULL_REQUEST_TEMPLATE.md` with comprehensive pre-merge checklist, change summary, and verification evidence sections.
  - Added `.github/ISSUE_TEMPLATE/feature_request.md` and `.github/ISSUE_TEMPLATE/bug_report.md`.
  - Added `CONTRIBUTING.md` outlining Conventional Commits, branch naming, local setup, pre-commit verification, and PR review workflow.
- **Security Hardening:**
  - Production-ready security headers (`SecurityHeadersMiddleware`: CSP, Referrer-Policy, Permissions-Policy), HSTS, SSL redirect, secure session/CSRF cookies, and `X_FRAME_OPTIONS = 'DENY'`.
  - Profile avatar upload sanitization, format verification with PIL, and 5MB size limit.

### Changed
- **CSS Layer Hierarchy Architecture:** Declared `@layer theme, legacy, components, utilities;` in `input.css` and encapsulated entire legacy `theme.css` in `@layer legacy { ... }` preserving CRLF line endings, allowing Tailwind utilities in `@layer utilities` to override legacy styling without `!important`.
- **Design Token & Accessibility Contrast Refinements:**
  - Upgraded `--text-muted` from `#888F9E` (~3.1:1) to `#646B7A` (~4.8:1/5.1:1) in Light mode and `#8E95A2` (~5.7:1) in Dark mode, ensuring full WCAG 2.1 AA compliance for body and meta text across both themes.
  - Scoped legacy CSS rules: declared legacy custom classes frozen in favor of Tailwind utility classes.
- **Header "Sign In" Button:** Restyled `.header-signin-btn` using Tailwind utilities while preserving required classes and accessible label.
- **Unified Product Card Adoption:** Replaced duplicated card markup across `templates/catalog/product_list.html`, `templates/home.html`, and `templates/catalog/product_detail.html` with `templates/includes/product_card.html`.
- **UI/UX Redesign — Calm, Editorial, Product-First Storefront (Phases 1, 2 & 3):**
  - Redesigned light (`#FAF9F6` / `#2B5B5F`) and dark (`#0F1012` / `#D8A65A`) palettes, fluid `Fraunces` + `Plus Jakarta Sans` typography, global header & 4-column footer, editorial home page, catalog showcase, product detail click-to-zoom gallery, 3-step checkout stepper, printable invoices, and inline-style-free auth views.
  - Resolved dark/light contrast issues in `.auth-showcase`, button resets, mobile/desktop search toggle visibility, and form labels.

### Removed
- **Primary Gradient:** Completely removed `--primary-gradient` token from `:root` and `[data-theme="dark"]`, converting `.auth-showcase` to solid Deep Teal to strictly adhere to design system prohibitions on gradients.
- **Dead Legacy Product Card CSS:** Deleted legacy `.product-card*`, `.quick-add*`, `.product-card-desc/meta/actions`, and mobile/touch card overrides from `static/css/theme.css`.

### Fixed
- **Stripe Webhook & PCI Hardening:** Enforced `STRIPE_WEBHOOK_SECRET` signature verification (rejecting unsigned requests with `400`), added webhook idempotency, switched real-key Stripe payments to Stripe Checkout Sessions, and added expiry validation on `CardPaymentForm`.
- **Checkout Concurrency & Data Integrity:** Locked `Coupon` rows with `select_for_update()` during checkout, restored coupon `times_used` on order cancellation, moved session clearing and email dispatch outside `transaction.atomic()`, preserved multiple guest orders in session (`guest_order_ids`), enforced `is_active=True` on checkout products, and changed `OrderItem.product` `on_delete` to `PROTECT`.
- **Cart & Catalog Performance:** Cached `Cart.coupon` per request, returned `400` JSON / error feedback on invalid `cart_add` submissions, and eliminated N+1 queries in `Product.average_rating` and `Product.get_rating_distribution()`.
- **CI Linting Compatibility:**
  - Removed redundant `#!/usr/bin/env python` shebang line from `manage.py` resolving Ruff `EXE001` (shebang on non-executable file) failure on Unix-based GitHub Actions runners.

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
