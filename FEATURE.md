# AuraStore E-Commerce Platform — Feature Inventory

> **Living Documentation:** This document tracks every feature implemented in the project.  
> **Mandatory Protocol:** Every newly implemented and verified feature must be automatically documented in this file in all future sessions and chats without requiring explicit user prompts.

---

## 📋 Feature Tracking Protocol

Whenever a feature, module, or enhancement is successfully implemented:
1. Append or update the feature entry under the appropriate category below.
2. Include the date of completion, technical description, key files modified/added, and verification status.
3. Keep the companion `README.md` file updated in tandem if the feature modifies user-facing capabilities, setup instructions, or environment variables.

---

## 🚀 Implemented Features

### 1. Core Architecture & Modern Tooling
- **Status:** Completed
- **Date:** November 2026
- **Description:**
  - Modern Python application structure utilizing **Python 3.12+** and **Django 6.1+**.
  - Fast package management via **Astral `uv`** with pinned dependencies in `pyproject.toml` and `uv.lock`.
  - Production-ready environment variable management with `django-environ` reading `.env` with fallback support.
  - Multi-database engine compatibility: Out-of-the-box configuration for PostgreSQL 18 via Docker Compose alongside SQLite fallback for local test/dev.
  - Strict linting and code quality enforcement with **Ruff** (`tool.ruff.lint.per-file-ignores` for migrations).
- **Key Files:**
  - `pyproject.toml`
  - `uv.lock`
  - `docker-compose.yaml`
  - `.env.example`
  - `core/settings.py`

---

### 2. Custom User Model & Accounts Schema
- **Status:** Completed
- **Date:** November 2026
- **Description:**
  - Replaced default Django `User` with `apps.accounts.models.CustomUser` extending `AbstractUser`.
  - Configured `AUTH_USER_MODEL = 'accounts.CustomUser'` from initial migration to ensure scalable user records.
  - Enforced unique email constraint (`email = models.EmailField(unique=True)`).
  - Added profile fields: `phone` (CharField), `birth_date` (DateField), and `profile_picture` (ImageField).
  - Registered in Django Admin with custom `CustomUserAdmin` exposing phone, active status, staff status, and fieldsets.
- **Key Files:**
  - `apps/accounts/models.py`
  - `apps/accounts/admin.py`
  - `apps/accounts/migrations/0001_initial.py`
  - `apps/accounts/migrations/0002_customuser_birth_date_customuser_phone_and_more.py`

---

### 3. Dual-Identifier Authentication Backend
- **Status:** Completed
- **Date:** November 2026
- **Description:**
  - Implemented `EmailOrUsernameModelBackend` in `apps.accounts.backends`.
  - Allows users to authenticate interchangeably using either their username or their email address.
  - Case-insensitive lookups (`iexact`) for both username and email to prevent user frustration.
  - Built-in timing attack resistance: triggers `UserModel().set_password(password)` dummy hasher when user lookup fails.
  - Registered alongside standard `ModelBackend` in `settings.AUTHENTICATION_BACKENDS`.
- **Key Files:**
  - `apps/accounts/backends.py`
  - `core/settings.py`

---

### 4. Custom Login Form with High-Empathy Feedback
- **Status:** Completed
- **Date:** November 2026
- **Description:**
  - Created `CustomLoginForm(forms.Form)` tailored for dual-identifier login.
  - Detailed field validation and customized error messages for missing identifiers or passwords.
  - Granular validation distinguishing between:
    - Inactive / deactivated accounts (`code="inactive"`).
    - Password mismatch / invalid credentials (`code="invalid_credentials"`).
    - Non-existent username or email (`code="user_not_found"`).
  - Semantic HTML attributes: `autocomplete`, `autocapitalize="none"`, `spellcheck="false"`, `aria-describedby`, and `aria-invalid`.
- **Key Files:**
  - `apps/accounts/forms.py`

---

### 5. Session Management & "Remember Me" Persistence
- **Status:** Completed
- **Date:** November 2026
- **Description:**
  - Added `remember_me` checkbox in login form.
  - When checked, session expiration is set to 30 days (`request.session.set_expiry(60 * 60 * 24 * 30)`).
  - When unchecked, session expires when the browser is closed (`request.session.set_expiry(0)`).
- **Key Files:**
  - `apps/accounts/forms.py`
  - `apps/accounts/views.py`

---

### 6. Secure Authentication Views & Redirection Flow
- **Status:** Completed
- **Date:** November 2026
- **Description:**
  - Class-based `CustomLoginView(View)` and `CustomLogoutView(View)`.
  - Redirects already-authenticated users away from the login page to the home dashboard.
  - **Open-Redirect Protection:** Validates `next` parameter using `url_has_allowed_host_and_scheme` to prevent phishing redirection.
  - Personalized flash messages using Django messages framework upon sign-in and sign-out.
  - Dual HTTP verb support for logout (both GET and POST).
- **Key Files:**
  - `apps/accounts/views.py`
  - `apps/accounts/urls.py`
  - `core/urls.py`

---

### 7. Design System & UI/UX Constitution (`DESIGN_SYSTEM.md`)
- **Status:** Completed
- **Date:** November 2026
- **Description:**
  - Full design system specification established in `DESIGN_SYSTEM.md`.
  - Comprehensive CSS token architecture: colors, semantic states, elevation shadows, border radii, and spacing.
  - Premium typography scale utilizing **Plus Jakarta Sans** with strict hierarchy from `display-1` down to `micro-badge`.
  - Mandatory verification checklist for visual consistency, contrast, and responsiveness.
- **Key Files:**
  - `DESIGN_SYSTEM.md`
  - `static/css/theme.css`

---

### 8. Zero-FOUC Dark & Light Theme Switcher
- **Status:** Completed
- **Date:** November 2026
- **Description:**
  - Seamless dark and light mode support with complete token inversion.
  - **Zero Flash of Unstyled Content (FOUC):** Synchronous theme resolution executed in the `<head>` of `base.html` before DOM painting.
  - Persists user preference in `localStorage` under key `ecommerce_theme_preference`.
  - Automatically respects OS-level system preferences via `window.matchMedia('(prefers-color-scheme: dark)')` with real-time listener.
  - Keyboard accessible toggle button with dynamic SVG icons (Sun / Moon) and ARIA attributes.
- **Key Files:**
  - `templates/base.html`
  - `static/js/theme.js`
  - `static/css/theme.css`

---

### 9. Accessible UI Components & Micro-Interactions
- **Status:** Completed
- **Date:** November 2026
- **Description:**
  - Interactive password visibility toggle (Eye / Eye-Off) without re-rendering or erasing input values.
  - Touch-friendly interactive targets meeting WCAG 2.1 AA minimums (≥ 44×44px).
  - Focus ring indicators (`:focus-visible`) across all buttons, inputs, and links.
  - Form submission loading state with animated spinner and duplicate-submission prevention (`aria-busy="true"`, button lock).
  - Accessible dismissable flash notification banners with micro-transitions.
  - "Skip to main content" accessibility link for keyboard/screen-reader navigation.
- **Key Files:**
  - `static/js/theme.js`
  - `static/css/theme.css`
  - `templates/base.html`
  - `templates/accounts/login.html`

---

### 10. Responsive Split-Screen Auth & Dashboard Templates
- **Status:** Completed
- **Date:** November 2026
- **Description:**
  - Split-screen modern login layout: left column featuring branded showcase highlights, right column hosting the custom auth form.
  - Fully responsive across mobile (320px+), tablet, and desktop breakpoints.
  - Centralized dashboard / landing page (`templates/home.html`) presenting user authentication state, account summary, design system indicators, and auth feature status.
- **Key Files:**
  - `templates/accounts/login.html`
  - `templates/home.html`
  - `templates/base.html`

---

### 11. Automated Test Suite (100% Pass Rate)
- **Status:** Completed
- **Date:** November 2026
- **Description:**
  - Initial 12 comprehensive unit and integration tests covering authentication, login, session persistence, and security controls.
- **Key Files:**
  - `apps/accounts/tests.py`

---

### 12. User Registration & Account Creation Flow
- **Status:** Completed
- **Date:** November 2026
- **Description:**
  - Implemented `CustomRegistrationForm` (`forms.ModelForm`) with:
    - Case-insensitive unique username and unique email validation.
    - Password confirmation matching and enforcement of Django's `validate_password` password validators.
    - Accessible styling conforming to `DESIGN_SYSTEM.md` with input icons, clear help text, and anchored field error alerts.
  - Implemented `RegisterView(View)`:
    - Renders split-screen showcase registration layout.
    - Automatically signs new users in upon successful registration with personalized welcome banner.
    - Open-redirect mitigation on post-registration `next` destination.
    - Redirects already-authenticated users to home dashboard.
  - Implemented `templates/accounts/register.html` matching `DESIGN_SYSTEM.md`:
    - Responsive split-screen desktop/tablet showcase column with member benefit highlights and quote.
    - Accessible password visibility toggles (`data-target`) for both password and password-confirmation inputs.
    - Zero-FOUC architecture inheriting synchronous theme detection from `base.html`.
- **Key Files:**
  - `apps/accounts/forms.py`
  - `apps/accounts/views.py`
  - `apps/accounts/urls.py`
  - `templates/accounts/register.html`
  - `templates/base.html`
  - `templates/accounts/login.html`

---

### 13. User Profile Management & Avatar Uploads
- **Status:** Completed
- **Date:** November 2026
- **Description:**
  - Implemented `UserProfileForm` (`forms.ModelForm` for `CustomUser`):
    - Profile fields: `first_name`, `last_name`, `phone`, `birth_date`, and `profile_picture` avatar upload.
    - Phone number character and format validation with maximum 15-character constraint.
    - Clean date widget and file input formatting with image format guidance.
  - Implemented `ProfileView(LoginRequiredMixin, View)`:
    - Secure endpoint requiring authentication (`login_url="login"`).
    - Multipart form processing (`request.FILES`) for avatar uploads.
    - Instant user feedback via Django messages framework upon successful profile updates.
  - Implemented `templates/accounts/profile.html`:
    - Profile header card featuring round avatar display with fallback user initials badge.
    - Form card with responsive 2-column layout for name and contact info.
    - Non-editable display of registered Username ID and Email address.
    - Direct link to password reset workflow.
- **Key Files:**
  - `apps/accounts/forms.py`
  - `apps/accounts/views.py`
  - `apps/accounts/urls.py`
  - `templates/accounts/profile.html`
  - `static/css/theme.css`
  - `templates/base.html`

---

### 14. Password Reset & Recovery Workflow
- **Status:** Completed
- **Date:** November 2026
- **Description:**
  - End-to-end 4-step secure password recovery workflow using Django auth view architecture:
    - `CustomPasswordResetView` (`/password-reset/`, name=`password_reset`): Initiates reset request via email with case-insensitive user lookup.
    - `CustomPasswordResetDoneView` (`/password-reset/done/`, name=`password_reset_done`): Confirmation notification screen with delivery guidance.
    - `CustomPasswordResetConfirmView` (`/reset/<uidb64>/<token>/`, name=`password_reset_confirm`): Secure token verification with new password inputs and visibility toggles; graceful handling of invalid/expired tokens.
    - `CustomPasswordResetCompleteView` (`/reset/done/`, name=`password_reset_complete`): Final celebration and prompt to sign in with new credentials.
  - Dedicated forms: `CustomPasswordResetForm` and `CustomSetPasswordForm` with full `DESIGN_SYSTEM.md` token integration.
  - Configured console email backend default (`EMAIL_BACKEND`) for dev/test environments.
  - Clean email notification templates: `password_reset_email.html` and `password_reset_subject.txt`.
- **Key Files:**
  - `apps/accounts/views.py`
  - `apps/accounts/forms.py`
  - `apps/accounts/urls.py`
  - `core/settings.py`
  - `templates/accounts/password_reset_form.html`
  - `templates/accounts/password_reset_done.html`
  - `templates/accounts/password_reset_confirm.html`
  - `templates/accounts/password_reset_complete.html`
  - `templates/accounts/password_reset_email.html`
  - `templates/accounts/password_reset_subject.txt`

---

### 15. Comprehensive 30-Test Automated Suite (100% Pass Rate)
- **Status:** Completed
- **Date:** November 2026
- **Description:**
  - Expanded test suite from 12 to 30 unit and integration tests across 4 test classes:
    - `AuthenticationAndLoginTests` (12 tests): Login, case-insensitivity, remember-me session persistence, open-redirect defenses, logout.
    - `UserRegistrationTests` (7 tests): Page rendering, authenticated user redirect, successful registration, duplicate email rejection, duplicate username rejection, password mismatch error, weak password policy rejection.
    - `UserProfileManagementTests` (5 tests): Unauthenticated redirect, profile view rendering, successful field updates, invalid phone validation, avatar image upload with `SimpleUploadedFile`.
    - `PasswordResetWorkflowTests` (6 tests): Reset form rendering, email dispatch verification, done page rendering, token confirmation & password update verification, invalid/expired token handling, complete page rendering.
  - 100% pass rate verified via `uv run python manage.py test apps.accounts`.
- **Key Files:**
  - `apps/accounts/tests.py`

---

### 16. Product Catalog, Categories & Gallery System
- **Status:** Completed
- **Date:** November 2026
- **Description:**
  - **Data Models:**
    - `Category`: Categorization hierarchy with `name`, `slug` (unique), `description`, optional `image`, and `is_active` toggle.
    - `Product`: Comprehensive product entity with `category` foreign key, `name`, `slug` (unique), `description`, `price`, `sku` (unique), `stock`, `is_active`, `featured`, `created_at`, and `updated_at`. Optimized with database indexes on `slug`, `sku`, and `-created_at`.
    - `ProductImage`: Multi-image support for each product with `image` upload, `alt_text`, and `is_primary` flag.
  - **Business Logic & Properties:**
    - `Product.is_in_stock`: Dynamic boolean property checking inventory availability (`stock > 0`).
    - `Product.primary_image`: Intelligent image lookup returning designated primary image or first available gallery image with graceful fallback.
  - **Django Admin Interface:**
    - `CategoryAdmin`: List display with dynamic annotated product count, filter by active status, search by name/slug/description, and auto-populated slug.
    - `ProductAdmin`: Inline image editing with `ProductImageInline` (tabular), list display with price, stock, active and featured status, date hierarchy, search, and list-editable fields.
    - `ProductImageAdmin`: Media asset management with primary image filtering and product search.
  - **Views & Controller Flow:**
    - `ProductListView` (`/products/`): Dual category filtering (via dedicated URL path `/products/category/<slug>/` or `?category=<slug>`), full-text search across title, description, and SKU (`?q=`), sorting (newest, price ascending/descending, name A-Z), featured filter, active category chips with live count badges, and pagination (12 items per page).
    - `ProductDetailView` (`/products/<slug>/`): Dedicated product showcase featuring interactive thumbnail image switcher, stock badge, pricing, SKU and category metadata, full description, quantity selector, "Add to Cart" action, and related products grid.
  - **Design System & Accessibility (WCAG 2.1 AA):**
    - Semantic HTML with `<nav aria-label="Breadcrumb">`, `<form role="search">`, and distinct headings.
    - All interactive controls (filter chips, sort dropdown, search inputs, pagination links, thumbnail selectors) strictly satisfy minimum touch targets of ≥ 44×44px.
    - Flawless rendering in both Light and Dark modes with smooth transitions and glowing `:focus-visible` rings.
    - Zero Flash of Unstyled Content (FOUC).
  - **Automated Test Coverage:**
    - 23 unit and integration tests in `apps/catalog/tests.py` verifying model constraints, property methods, admin configurations, list filtering, keyword searching, sorting, pagination, detail view rendering, related products, 404 error boundaries, and uniqueness integrity.
- **Key Files:**
  - `apps/catalog/apps.py`
  - `apps/catalog/models.py`
  - `apps/catalog/admin.py`
  - `apps/catalog/views.py`
  - `apps/catalog/urls.py`
  - `apps/catalog/tests.py`
  - `apps/catalog/migrations/0001_initial.py`
  - `templates/catalog/product_list.html`
  - `templates/catalog/product_detail.html`
  - `core/settings.py`
  - `core/urls.py`
  - `static/css/theme.css`
  - `templates/base.html`
  - `templates/home.html`

---

### 17. Persistent Shopping Cart Engine & Dynamic Context Processor
- **Status:** Completed
- **Date:** November 2026
- **Description:**
  - **Session-Backed Cart Engine (`apps/cart/cart.py`):**
    - High-performance, lightweight session storage engine (`Cart`) decoupling shopping cart persistence from database roundtrips.
    - Full API implementation:
      - `add(product, quantity=1, override_quantity=False)`: Adds new items or increments/overrides existing item quantities with catalog price validation and bounds checking.
      - `remove(product)`: Removes product keys from session with automated state synchronization.
      - `get_total_price()`: Computes total line item costs as standard Decimals.
      - `get_item_count()` & `__len__()`: Returns total quantity of units across all cart items.
      - `clear()`: Empties session cart state and cleans memory references.
      - `__iter__()`: Yields live Product database instances linked with calculated line item costs, automatically purging stale keys if products are deleted from catalog.
  - **Global Context Processor (`apps/cart/context_processors.py`):**
    - `cart(request)` provides global `cart` instance across all Django templates.
    - Injects dynamic live item count badge and direct cart link into the global navbar header (`templates/base.html`).
  - **Cart Views & Controller Logic (`apps/cart/views.py`):**
    - `cart_detail` (`/cart/`): Full cart breakdown showing product thumbnails, titles, SKUs, categories, unit prices, responsive quantity toggles, line totals, free shipping indicators, estimated taxes, order summary, and checkout CTA.
    - `cart_add` (`/cart/add/<product_id>/`): Validates stock levels, handles both standard form submissions and asynchronous AJAX requests, clamps quantities to maximum available stock when requests exceed inventory, and emits feedback notifications.
    - `cart_remove` (`/cart/remove/<product_id>/`): Removes items with flash messages and supports AJAX responses with updated cart totals and count.
    - `cart_update_quantity` (`/cart/update/<product_id>/`): Supports direct input and increment/decrement actions with stock boundary enforcement.
  - **Design System & Accessibility (WCAG 2.1 AA):**
    - Built with responsive 2-column layout (`.cart-layout-grid`) collapsing smoothly on mobile viewports.
    - Empty cart state with modern illustration, descriptive guidance, and catalog navigation CTA.
    - Touch targets ≥ 44×44px for quantity increment/decrement controls, table actions, and checkout CTA.
    - Zero Flash of Unstyled Content (FOUC), glowing `:focus-visible` outlines, and full light/dark theme support.
  - **Automated Test Coverage:**
    - 14 comprehensive unit and integration tests in `apps/cart/tests.py` verifying cart initialization, adding, incrementing, overriding, removing, price calculations, iteration cleanup, clearing, context processor injection, empty view rendering, standard/AJAX add, out-of-stock rejection, stock clamping, quantity updates, and removal.
- **Key Files:**
  - `apps/cart/apps.py`
  - `apps/cart/cart.py`
  - `apps/cart/context_processors.py`
  - `apps/cart/forms.py`
  - `apps/cart/views.py`
  - `apps/cart/urls.py`
  - `apps/cart/tests.py`
  - `templates/cart/cart_detail.html`
  - `templates/base.html`
  - `templates/catalog/product_detail.html`
  - `core/settings.py`
  - `core/urls.py`
  - `static/css/theme.css`

---

### 18. Orders Management, Atomic Checkout & Customer Invoicing Portal
- **Status:** Completed
- **Date:** November 2026
- **Description:**
  - **Data Models (`apps/orders/models.py`):**
    - `Order`: Captures customer credentials, shipping address, order number (auto-generated unique `ORD-<HEX>` slug), fulfillment status (`pending`, `processing`, `paid`, `shipped`, `delivered`, `cancelled`), payment status, and timestamps. Indexed by `-created_at`, `order_number`, and `status`. Supports both authenticated users and guest checkout (`user=None`).
    - `OrderItem`: Line item model linking `Order` and `Product` with captured purchase `price` (DecimalField), `quantity`, and `get_cost()` calculation.
  - **Checkout Form & Views (`apps/orders/views.py`):**
    - `order_create` (`/orders/create/`):
      - Rejects checkout attempts with empty carts.
      - Prepopulates contact and shipping information for authenticated customers.
      - Executes inside a strict `transaction.atomic()` database block with `select_for_update()` product locking to prevent concurrent inventory overselling.
      - Atomically decrements product inventory stock, creates Order and OrderItems, clears the session cart, and redirects to order confirmation.
      - Automated rollback protection if any item stock becomes insufficient during checkout.
    - `order_created` (`/orders/created/<order_id>/`): Confirmation screen rendering successful order placement notice, reference details, and printable invoice. Protected by user ownership and session access controls.
    - `order_list` (`/orders/my-orders/`): Login-required customer dashboard displaying full order history, status badges, payment indicators, line item previews, and status filter pills.
    - `order_detail` (`/orders/<order_number>/`): Formal order invoice view with customer details, itemized table, billing breakdown, print-ready CSS (`@media print`), and permission enforcement.
  - **Django Admin Enhancements (`apps/orders/admin.py`):**
    - Tabular `OrderItemInline` with product lookups and calculated item costs.
    - Custom admin actions: `mark_as_paid`, `mark_as_shipped`, and `mark_as_delivered` with user notification messages.
    - Filtering by status, payment, and creation date, with search by order number, customer name, email, and phone.
  - **Design System & Accessibility (WCAG 2.1 AA):**
    - Two-column checkout layout with sticky order summary and item thumbnail previews.
    - Form inputs with autocomplete attributes, inline error indicators, and high contrast.
    - Print-ready invoice stylesheets stripping navigation and backgrounds during browser print (`@media print`).
    - Flawless dark and light theme compliance.
  - **Automated Test Coverage:**
    - 15 comprehensive unit and integration tests in `apps/orders/tests.py` verifying model creation, auto-generated order numbers, line item costs, total calculations, empty cart protection, authenticated prepopulation, atomic checkout stock reduction, concurrency rollback on insufficient stock, access control permissions, order history listing and status filtering, invoice views, and admin bulk actions.
- **Key Files:**
  - `apps/orders/apps.py`
  - `apps/orders/models.py`
  - `apps/orders/forms.py`
  - `apps/orders/views.py`
  - `apps/orders/urls.py`
  - `apps/orders/admin.py`
  - `apps/orders/tests.py`
  - `apps/orders/migrations/0001_initial.py`
  - `templates/orders/order_create.html`
  - `templates/orders/order_created.html`
  - `templates/orders/order_list.html`
  - `templates/orders/order_detail.html`
  - `core/settings.py`
  - `core/urls.py`
  - `static/css/theme.css`

---

### 19. Defense-in-Depth Security Hardening, File Upload Protection & Modern Security Headers
- **Status:** Completed
- **Date:** November 2026
- **Description:**
  - **Deployment Security Hardening:**
    - Configured production-grade security settings in `core/settings.py` backed by environment variable overrides (`django-environ`).
    - Configured `SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=False)`.
    - Enforced HTTP Strict Transport Security (HSTS): `SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=31536000 if not DEBUG else 0)`, `SECURE_HSTS_INCLUDE_SUBDOMAINS = True`, and `SECURE_HSTS_PRELOAD = True`.
    - Enforced secure session and CSRF cookie flags: `SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=not DEBUG)` and `CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=not DEBUG)`.
    - Restricted session cookie script access via `SESSION_COOKIE_HTTPONLY = True` and preserved frontend compatibility with `CSRF_COOKIE_HTTPONLY = False`.
    - Protected against cross-site request forgery attacks with `SESSION_COOKIE_SAMESITE = 'Lax'` and `CSRF_COOKIE_SAMESITE = 'Lax'`.
    - Enabled content sniffing prevention `SECURE_CONTENT_TYPE_NOSNIFF = True`, cross-site scripting filter `SECURE_BROWSER_XSS_FILTER = True`, and clickjacking defense `X_FRAME_OPTIONS = 'DENY'`.
  - **Modern Security Headers Middleware:**
    - Engineered `core.middleware.SecurityHeadersMiddleware` and registered it in `MIDDLEWARE`.
    - Attached defense-in-depth headers on all HTTP responses:
      - `Content-Security-Policy`: Restricts scripts, styles, fonts, and connects, while permitting designated Google Fonts origins (`fonts.googleapis.com`, `fonts.gstatic.com`) and blocking framing via `frame-ancestors 'none'`.
      - `Referrer-Policy`: Strict policy (`strict-origin-when-cross-origin`) to safeguard user privacy across navigations.
      - `Permissions-Policy`: Restricts browser hardware access (`camera=(), microphone=(), geolocation=(), payment=(), usb=()`).
  - **Avatar File Upload Sanitization & Hardening:**
    - Hardened `UserProfileForm.clean_profile_picture` in `apps/accounts/forms.py`.
    - Enforced maximum avatar file size ceiling of 5MB (`5 * 1024 * 1024` bytes).
    - Whitelisted valid image extensions strictly to `.jpg`, `.jpeg`, `.png`, and `.webp`.
    - Implemented binary header inspection and integrity checks using Pillow (`Image.open()` and `verify()`), proactively rejecting dangerous payloads including disguised SVG XSS vectors, scripts, executables, and corrupted files.
    - Implemented file stream rewind (`seek(0)`) to maintain clean storage persistence.
  - **Open-Redirect Defenses:**
    - Verified and tested `CustomLoginView` and `RegisterView` redirect parameters against `url_has_allowed_host_and_scheme()`. Untrusted external domains or arbitrary schemes are discarded in favor of default internal landing routes.
  - **Security Documentation & Policies:**
    - Created comprehensive `SECURITY.md` detailing supported versions, vulnerability disclosure SLA and protocol, architecture defenses, and testing procedures.
  - **Automated Verification:**
    - Created 23 automated tests in `apps/accounts/tests_security.py` verifying headers, secure cookies, upload boundaries, format validation, and open-redirect defenses.
    - Verified all test suites in the workspace pass cleanly.
    - Verified deploy check passes with zero warnings (`uv run python manage.py check --deploy`).
    - Verified Ruff linter clean pass (`uv run ruff check .`).
- **Key Files:**
  - `core/settings.py`
  - `core/middleware.py`
  - `apps/accounts/forms.py`
  - `apps/accounts/tests_security.py`
  - `SECURITY.md`
  - `.env.example`
  - `README.md`
  - `FEATURE.md`

---

### 20. GitOps Automation, CI/CD Pipelines & Repository Standardization
- **Status:** Completed
- **Date:** November 2026
- **Description:**
  - **Pre-commit Automation:**
    - Configured `.pre-commit-config.yaml` with Astral Ruff (linting with `--fix` and `ruff-format`), alongside standard safety hooks (`check-yaml`, `end-of-file-fixer`, `trailing-whitespace`, `check-merge-conflict`, `detect-private-key`).
  - **CI/CD GitHub Actions Workflows:**
    - Created `.github/workflows/ci.yml`: Multi-step pipeline executing Ruff linting and formatting check, Django deployment security check (`manage.py check --deploy`), and full Django test suite on Python 3.12 with Astral `uv` caching.
    - Resolved cross-platform CI Ruff linting failure (`EXE001`) by removing the redundant shebang header from `manage.py`.
    - Created `.github/workflows/security.yml`: Continuous vulnerability monitoring with `pip-audit` for dependency analysis and TruffleHog OSS for credential/secret detection.
  - **Developer Workflow & Contribution Standards:**
    - Established `.github/PULL_REQUEST_TEMPLATE.md` with pre-merge checklist, verification evidence, and documentation synchronization enforcement.
    - Standardized `.github/ISSUE_TEMPLATE/feature_request.md` and `.github/ISSUE_TEMPLATE/bug_report.md` for consistent defect tracking and feature proposals.
    - Authored `CONTRIBUTING.md` enforcing the Conventional Commits 1.0.0 standard, branch naming schemes (`feature/*`, `fix/*`, `chore/*`), local development setup with `uv`, pre-commit hooks, and PR review lifecycles.
    - Authored `CHANGELOG.md` following Keep a Changelog and Semantic Versioning (SemVer 2.0.0) standard, detailing milestone releases `v0.1.0` and `v0.2.0`, alongside unreleased enhancements.
- **Key Files:**
  - `.pre-commit-config.yaml`
  - `.github/workflows/ci.yml`
  - `.github/workflows/security.yml`
  - `.github/PULL_REQUEST_TEMPLATE.md`
  - `.github/ISSUE_TEMPLATE/feature_request.md`
  - `.github/ISSUE_TEMPLATE/bug_report.md`
  - `CONTRIBUTING.md`
  - `CHANGELOG.md`
  - `manage.py`

---

### 21. Modern Editorial UI/UX Storefront Redesign (Phases 1, 2 & 3)
- **Status:** Completed
- **Date:** November 2026
- **Description:**
  - **Calm, Neutral-First Theme Tokens:** Redesigned color palette to put product photography first. Light theme features warm off-white page (`#FAF9F6`), crisp white surfaces (`#FFFFFF`), neutral text (`#16181D`), and a deep teal accent (`#2B5B5F`, hover `#224A4D`). Dark theme features warm charcoal (`#0F1012`), elevated surfaces (`#16181C`, `#1D2025`), neutral light text (`#F2F0EB`), and muted amber accent (`#D8A65A`).
  - **Editorial Typography Scale with Fluid Clamp:** Loaded Google Fonts `Fraunces` serif alongside `Plus Jakarta Sans` with `font-display: swap`. Implemented fluid type scale via `clamp()` across hero display, page H1, section H2, and card titles. Enforced tabular numerals for price tags and 65ch max-line-length constraints.
  - **Global Header & Navigation:** Slimmer solid header with hairline border on scroll (`.header-scrolled`), desktop-inline and mobile-expandable search bar, responsive 44×44px theme toggle, accessible skip link, and shopping cart counter with dynamic bump animation.
  - **Editorial Storefront Home Page:** Replaced developer-facing showcase cards with a calm editorial hero, curated "Featured Objects" grid with 4:5 image ratio, secondary gallery image hover crossfade, and AJAX quick-add button, followed by category tiles and authentic trust pillars. Maintained personalized authenticated member banner with 100% test assertion compatibility.
  - **Product Catalog Showcase (Phase 2):** Overhauled `product_list.html` with breadcrumbs, search/sort toolbar, horizontally scrollable category chips with scroll-snap on mobile, responsive 4:5 image grid (2 col mobile, 3 col tablet, 4 col desktop), secondary image hover crossfade, quick-add buttons, and styled zero-result empty state.
  - **Product Detail Showcase (Phase 2):** Overhauled `product_detail.html` with desktop sticky gallery, pure CSS click-to-zoom (`scale(1.6)` with smooth transition, no CDN library), interactive thumbnail switcher, sticky buy box with quantity stepper, single dominant CTA, reassuring microcopy, accessible 3-tab specifications panel, and related products rail.
  - **Shopping Cart & Checkout Flow (Phase 3):** Enhanced `cart_detail.html` and `order_create.html` with a clear 3-step progress stepper (`Cart → Checkout → Confirmation`), responsive 2-column layout with sticky summary on desktop, and a mobile-collapsible order summary with smooth toggle on screens ≤ 960px.
  - **Customer Portal & Printable Invoices (Phase 3):** Refined `order_list.html`, `order_created.html`, and `order_detail.html` with calm editorial headers, status badges, and an updated print stylesheet (`@media print`) rendering clean `#000000` text with zero background fills and hidden chrome.
  - **Authentication & Account Views (Phase 3):** Refined `login.html`, `register.html`, `profile.html`, and all four password reset step templates (`password_reset_form.html`, `password_reset_done.html`, `password_reset_confirm.html`, `password_reset_complete.html`). Fully eliminated all inline `style="..."` attributes across all templates in the repository, replacing them with semantic CSS classes while strictly preserving all test assertions and element IDs.
  - **Comprehensive Multi-Column Footer:** Responsive 4-column footer providing clear navigation across Collections, Customer Care, Member Accounts, and brand commitments.
  - **CSS Architecture & Standards:** Added `.u-sr-only` definition, removed hard-coded hex in select arrow tokens using CSS custom properties, deduplicated `.form-grid-2`, and defined utility classes (`btn-lg`, `btn-outline`, `badge-primary`, `badge-error`, `text-primary`, `text-success`, `form-helper`, `optional-mark`, `invoice-actions`, `badge-info`, `auth-callout-box`, `status-icon-centered`, `summary-mobile-toggle`).
- **Key Files:**
  - `DESIGN_SYSTEM.md`
  - `templates/base.html`
  - `templates/home.html`
  - `templates/catalog/product_list.html`
  - `templates/catalog/product_detail.html`
  - `templates/cart/cart_detail.html`
  - `templates/orders/order_create.html`
  - `templates/orders/order_created.html`
  - `templates/orders/order_detail.html`
  - `templates/orders/order_list.html`
  - `templates/accounts/login.html`
  - `templates/accounts/register.html`
  - `templates/accounts/profile.html`
  - `templates/accounts/password_reset_form.html`
  - `templates/accounts/password_reset_done.html`
  - `templates/accounts/password_reset_confirm.html`
  - `templates/accounts/password_reset_complete.html`
  - `static/css/theme.css`
  - `static/js/theme.js`
  - `apps/accounts/views.py`
  - `CHANGELOG.md`
- **Verification:**
  - `uv run python manage.py test` passed 105/105 tests (100% pass rate).
  - `uv run ruff check .` passed with 0 errors.

---

### 22. Comprehensive Dark & Light Theme Contrast & Cross-Theme Legibility Fixes
- **Status:** Completed
- **Date:** November 2026
- **Description:**
  - **Full Contrast & Invisibility Audit:** Diagnosed and corrected critical text and component contrast issues in both Light and Dark modes.
  - **Auth Showcase Column Resolution:** Replaced undefined/transparent background fallbacks and improper `--text-inverse` assignments in `.auth-showcase` (which previously produced 100% invisible white-on-white text in Light mode and near-black on dark charcoal in Dark mode). Configured rich Deep Teal gradient (`#1A3E42` to `#2B5B5F`) with crisp `#FFFFFF` text in Light mode, and elevated charcoal (`#1D2025`) with crisp `#F2F0EB` text and muted amber (`#D8A65A`) accents in Dark mode.
  - **Native Button Reset & Icon Box Elimination:** Fixed browser-default `buttonface` light-grey bevel styling on `.password-toggle-btn` and header `.search-toggle-btn` by applying a universal button reset (`background: transparent; border: none; padding: 0; color: inherit;`) and explicit styles on action buttons.
  - **Desktop vs Mobile Search Button Visibility:** Corrected cascade specificity where `.header-action-btn` was overriding `.search-toggle-btn { display: none; }` on desktop viewports, properly hiding the mobile search toggle on desktop while keeping it active on mobile (`<= 640px`).
  - **Token Architecture & Contrast Unification:** Defined missing `--font-display`, `--primary-contrast`, and `--primary-gradient` across `:root` and `[data-theme="dark"]`. Replaced problematic uses of `var(--text-inverse)` on checkboxes, badges, and filter pills with `var(--primary-contrast)`, guaranteeing WCAG 2.1 AA compliance across both themes.
  - **Form Label Contrast Upgrade:** Promoted `.form-label` to `color: var(--text-primary); font-weight: 600;` for immediate visual prominence.
- **Key Files:**
  - `static/css/theme.css`
  - `templates/base.html`
  - `DESIGN_SYSTEM.md`
  - `FEATURE.md`
  - `README.md`
  - `CHANGELOG.md`
- **Verification:**
  - `uv run python manage.py test` passed 105/105 tests with zero regressions.
  - `uv run ruff check .` passed with 0 errors.

---

### 23. Tailwind CSS v4 Build Pipeline & Unified Product Card Component (Proof of Concept)
- **Status:** Completed
- **Date:** November 2026
- **Description:**
  - **Option A Architectural Pattern:** Integrated Tailwind CSS v4 directly with Django server-rendered templates, avoiding client-side React/shadcn complexity while maintaining maximum rendering performance and zero runtime Node requirements.
  - **Zero-Node Production Deployment:** Added root `package.json` with devDependencies `@tailwindcss/cli` and `tailwindcss`. Configured `npm run build:css` and `npm run watch:css`. Compiles `static/css/tailwind/input.css` into `static/css/app.css` which is committed to source control for native Python-only deployments.
  - **CSS Layer Architecture:** Declared `@layer theme, legacy, components, utilities;` at the stylesheet top. Fully encapsulated legacy `theme.css` (~4,500 lines) within `@layer legacy { ... }` with strict CRLF line ending preservation, ensuring Tailwind utility classes in `@layer utilities` override legacy rules cleanly without `!important` wars.
  - **Single Source of Truth Token Mapping:** Configured Tailwind `@theme` in `input.css` referencing existing CSS custom properties (`--color-page`, `--color-surface`, `--color-subtle`, `--color-ink`, `--color-ink-2`, `--color-ink-3`, `--color-line`, `--color-line-strong`, `--color-accent`, `--color-accent-hover`, `--color-accent-fg`, `--color-success*`, `--color-warning*`, `--color-error*`, `--radius-card`, `--radius-control`, `--font-body`, `--font-editorial`). Theme switching between light and dark operates automatically without duplicate `dark:` utility variants.
  - **Design Token & Contrast Fixes:** Corrected `--text-muted` from `#888F9E` (~3.1:1) to `#646B7A` (~4.8:1/5.1:1) in Light mode and `#8E95A2` (~5.7:1) in Dark mode, strictly fulfilling WCAG AA contrast for body/meta text. Completely excised `--primary-gradient` and converted `.auth-showcase` to solid Deep Teal adhering to `DESIGN_SYSTEM.md` gradient prohibitions.
  - **Unified Product Card Include:** Deduplicated card markup from `catalog/product_list.html`, `home.html`, and `catalog/product_detail.html` into a single reusable include `templates/includes/product_card.html`.
    - 4:5 aspect ratio with `aspect-[4/5]`, `bg-subtle`, and 500ms secondary gallery hover crossfade (`hover-img group-hover:opacity-100 motion-reduce:transition-none`).
    - Restrained semantic stock badges for out of stock and low stock (`<= 3`).
    - AJAX quick-add button revealed on desktop `group-hover` and `group-focus-within`, persistently visible on touch devices (`[@media(hover:none)]:opacity-100`).
    - Editorial typography: category uppercase eyebrow (`text-xs text-ink-3`), product title (`text-lg font-semibold text-ink`), clamped description (`line-clamp-2 max-w-prose text-ink-2`), tabular numerals price (`text-xl font-semibold tabular-nums text-ink`), and SKU demoted (`text-xs text-ink-3`).
    - Full-width secondary "View Details" button with 44px touch target (`h-11 rounded-control border-line-strong hover:bg-subtle`).
    - Complete cleanup of legacy `.product-card*`, `.quick-add*`, and `.product-card-desc/meta/actions` rules from `theme.css` without dead code.
  - **Header Sign-In Button Restyle:** Restyled `.header-signin-btn` using Tailwind utilities (`h-10 px-4 text-sm font-medium rounded-control border border-line-strong bg-surface text-ink hover:bg-subtle transition-colors shrink-0 whitespace-nowrap w-auto`) while preserving required classes `header-signin-btn`, `btn-label`, and `aria-label="Sign in"`.
- **Key Files:**
  - `package.json`
  - `.gitignore`
  - `static/css/tailwind/input.css`
  - `static/css/app.css`
  - `static/css/theme.css`
  - `templates/base.html`
  - `templates/includes/product_card.html`
  - `templates/home.html`
  - `templates/catalog/product_list.html`
  - `templates/catalog/product_detail.html`
  - `DESIGN_SYSTEM.md`
  - `README.md`
  - `FEATURE.md`
  - `CHANGELOG.md`
- **Verification:**
  - `uv run python manage.py test` passed 105/105 tests (100% pass rate).
  - `uv run ruff check .` passed with 0 errors.
  - `npm run build:css` successfully compiled minified `static/css/app.css`.
  - Content-Security-Policy suite (`apps.accounts.tests_security`) passed 23/23 tests.
  - Automated browser verification performed at 375px, 768px, and 1280px viewports across Light and Dark themes, verifying AJAX quick-add counter bump, theme toggle, mobile search expansion, and header scroll styling.

---

### 24. Stripe & Card Payment Gateway Integration
- **Status:** Completed
- **Date:** November 2026
- **Description:**
  - Integrated Stripe payment processing alongside Cash on Delivery (COD) payment method selector during checkout.
  - Added `payment_method` (`stripe` vs `cod`) and `stripe_payment_intent_id` to `Order` model with automated status transition method `mark_as_paid()`.
  - Created dedicated accessible `/orders/payment/<order_number>/` view and template with interactive card form (`cardholder_name`, `card_number`, `expiry`, `cvc`), 256-bit SSL encryption badge, and test-card sandbox support (`4242 4242 4242 4242`).
  - Supports simulated card declines (`4000 0000 0000 0002` / cards ending in `0002`) and optional switch to COD.
  - Configured `@csrf_exempt` Stripe webhook handler at `/orders/webhook/stripe/` for asynchronous `payment_intent.succeeded` events.
- **Key Files:**
  - `core/settings.py`
  - `.env.example`
  - `apps/orders/models.py`
  - `apps/orders/forms.py`
  - `apps/orders/views.py`
  - `apps/orders/urls.py`
  - `apps/orders/admin.py`
  - `templates/orders/order_payment.html`
  - `templates/orders/order_create.html`
  - `templates/orders/order_created.html`
  - `templates/orders/order_detail.html`
- **Verification:**
  - Comprehensive unit and integration tests covering checkout routing, valid card payment, declined card simulation, COD switching, unauthorized payment access rejection (403), and webhook processing.

---

### 25. Promotions & Coupon Discount System
- **Status:** Completed
- **Date:** November 2026
- **Description:**
  - Implemented `Coupon` model supporting both percentage-off (`percent`) and fixed-dollar-amount (`fixed`) discounts.
  - Comprehensive validation engine checking `is_active`, `valid_from` to `valid_to` time windows, `usage_limit` vs `times_used`, and minimum order subtotal spend (`min_purchase_amount`).
  - Integrated into session-backed `Cart` engine: `cart.coupon`, `cart.get_discount()`, `cart.get_total_price_after_discount()`, with endpoints `/cart/coupon/apply/` and `/cart/coupon/remove/`.
  - Added promo code redemption component to `cart_detail.html` with real-time feedback and active coupon removal pill.
  - Linked active coupon and calculated discount directly onto `Order` record upon checkout with atomic `times_used` incrementation.
- **Key Files:**
  - `apps/orders/models.py`
  - `apps/orders/admin.py`
  - `apps/cart/cart.py`
  - `apps/cart/views.py`
  - `apps/cart/urls.py`
  - `templates/cart/cart_detail.html`
  - `templates/orders/order_create.html`
  - `templates/orders/order_payment.html`
  - `templates/orders/order_created.html`
  - `templates/orders/order_detail.html`
- **Verification:**
  - `CouponIntegrationTestCase` covering percentage discounts, flat discounts, minimum spend enforcement, expiration rejection, cart session application, and order linkage.

---

### 26. Customer Product Reviews & Star Ratings
- **Status:** Completed
- **Date:** November 2026
- **Description:**
  - Created `Review` model attached to `Product` and `CustomUser` with 1–5 star ratings, headline title, feedback text, and unique constraint per user/product pair.
  - Automated Verified Purchase detection: cross-references customer's past paid orders to award `is_verified_purchase = True`.
  - Dynamic `average_rating`, `review_count`, and `rating_distribution` percentage calculations on `Product`.
  - Integrated visual star rating badges across unified `product_card.html` and `product_detail.html`.
  - Designed accessible review submission form and verified reviews showcase with rating distribution progress bars.
- **Key Files:**
  - `apps/catalog/models.py`
  - `apps/catalog/forms.py`
  - `apps/catalog/views.py`
  - `apps/catalog/urls.py`
  - `apps/catalog/admin.py`
  - `templates/catalog/product_detail.html`
  - `templates/includes/product_card.html`
- **Verification:**
  - `ReviewAndRatingTestCase` testing multi-review average calculations, distribution rounding, authenticated submissions, verified buyer detection, and unauthenticated redirects.

---

### 27. Customer Wishlist & Saved Items System
- **Status:** Completed
- **Date:** November 2026
- **Description:**
  - Created `Wishlist` model linked one-to-one with `CustomUser` with many-to-many relationship to `Product`.
  - Interactive wishlist heart toggle button on product cards (`product_card.html`) and product detail page (`product_detail.html`) supporting both AJAX JSON response and standard POST fallback.
  - Dedicated customer portal page at `/products/wishlist/` with product cards, stock status, direct "Move to Cart" button, and quick remove actions.
  - Added accessible Wishlist shortcut link in header navigation for authenticated customers.
- **Key Files:**
  - `apps/catalog/models.py`
  - `apps/catalog/views.py`
  - `apps/catalog/urls.py`
  - `apps/catalog/admin.py`
  - `templates/catalog/wishlist.html`
  - `templates/includes/product_card.html`
  - `templates/catalog/product_detail.html`
  - `templates/base.html`
- **Verification:**
  - `WishlistTestCase` validating toggle addition and removal, JSON response format, customer portal rendering, and unauthenticated redirects.

---

### 28. Saved Customer Address Book & Checkout Auto-Fill
- **Status:** Completed
- **Date:** November 2026
- **Description:**
  - Created `Address` model linked to `CustomUser` with default shipping address management (`is_default`).
  - Added "Save this address to my address book for faster checkout" checkbox to `OrderCreateForm`.
  - Authenticated checkout auto-fills from customer's default address and provides 1-click quick-select chips for stored addresses.
  - Registered `AddressInline` in `CustomUserAdmin` and dedicated `AddressAdmin`.
- **Key Files:**
  - `apps/accounts/models.py`
  - `apps/accounts/admin.py`
  - `apps/orders/forms.py`
  - `apps/orders/views.py`
  - `templates/orders/order_create.html`
- **Verification:**
  - Tested automated address creation upon order placement and pre-population into checkout forms.

---

### 29. Order Cancellation with Atomic Inventory Replenishment
- **Status:** Completed
- **Date:** November 2026
- **Description:**
  - Implemented `/orders/cancel/<order_number>/` endpoint allowing customers to cancel orders that are in `pending` state.
  - Concurrency-safe atomic rollback: uses `transaction.atomic()` and `select_for_update()` to restore product inventory units back into `Product.stock`.
  - Added accessible "Cancel Order" button with confirmation prompt on order detail view for authorized order owners.
  - Access controls prevent unauthorized cancellation attempts (403) and reject cancellation on non-pending orders.
- **Key Files:**
  - `apps/orders/views.py`
  - `apps/orders/urls.py`
  - `templates/orders/order_detail.html`
- **Verification:**
  - Automated unit tests confirming stock restoration, status transition to `cancelled`, and permission rejection.

---

### 30. Transactional Order Confirmation Receipt Emails
- **Status:** Completed
- **Date:** November 2026
- **Description:**
  - Automated dispatch of itemized order confirmation receipts in both styled HTML and clean plaintext formats upon order placement (COD) or payment confirmation (Stripe).
  - Outbox includes order number, item descriptions, SKUs, line item totals, subtotal, discount, shipping, total amount, and shipping destination details.
  - Uses `EmailMultiAlternatives` with `fail_silently=True` to guarantee checkout flow continuity.
- **Key Files:**
  - `apps/orders/views.py`
  - `templates/orders/emails/order_confirmation.txt`
  - `templates/orders/emails/order_confirmation.html`
- **Verification:**
  - `test_order_confirmation_email_sent_on_checkout` verifying subject, recipient, itemization, and body rendering.

---

### 31. Database Seeding Command (`python manage.py seed_db`)
- **Status:** Completed
- **Date:** November 2026
- **Description:**
  - Built comprehensive CLI management command `seed_db` in `apps/catalog/management/commands/seed_db.py`.
  - Populates 5 curated categories, 9 high-fidelity products with full editorial copy, sample customer reviews, promotional coupons (`WELCOME10`, `SAVE20`, `FLAT25`), and a demo customer account (`customer@aurastore.com` / `Password123!`) with a saved address.
- **Key Files:**
  - `apps/catalog/management/commands/seed_db.py`
- **Verification:**
  - Executed `uv run python manage.py seed_db` successfully initializing sample catalog and demo account.

---

### 32. Security, Concurrency & Query Hardening Audit Fixes
- **Status:** Completed
- **Date:** November 2026
- **Description:**
  - **Stripe Webhook & PCI Hardening (`apps/orders/views.py`, `apps/orders/forms.py`):** Enforced mandatory `STRIPE_WEBHOOK_SECRET` signature verification (rejecting unsigned webhooks with `400`), added idempotency (`if not order.paid:`) and email dispatch on webhook fulfillment, switched real-key Stripe payments to PCI-compliant `stripe.checkout.Session.create()` redirects, and added `CardPaymentForm.clean_expiry()` date validation and `OrderCreateForm.clean_payment_method()` fallback.
  - **Concurrency & Transaction Boundaries (`apps/orders/views.py`, `apps/orders/models.py`):** Locked `Coupon` rows with `select_for_update()` during `order_create` and restored `times_used` on `order_cancel`; moved `cart.clear()`, guest session tracking (`guest_order_ids` list supporting multiple guest orders), and email dispatch outside `transaction.atomic()`; enforced `is_active=True` during checkout; changed `OrderItem.product` `on_delete` from `CASCADE` to `PROTECT` (`0004_orderitem_protect_product.py`).
  - **Cart & Catalog Optimization (`apps/cart/cart.py`, `apps/cart/views.py`, `apps/catalog/models.py`):** Cached `Cart.coupon` per request, added 400/error handling for invalid `cart_add` submissions, and eliminated N+1 queries in `Product.average_rating` and `Product.get_rating_distribution()` using `Avg`/`Count` aggregation.
  - **Email Configuration (`core/settings.py`, `.env.example`):** Explicitly configured `DEFAULT_FROM_EMAIL`.
- **Key Files:**
  - `apps/orders/views.py`, `apps/orders/forms.py`, `apps/orders/models.py`, `apps/orders/migrations/0004_orderitem_protect_product.py`, `apps/orders/tests.py`
  - `apps/cart/cart.py`, `apps/cart/views.py`, `apps/cart/tests.py`
  - `apps/catalog/models.py`, `apps/catalog/tests.py`
  - `core/settings.py`, `.env.example`
- **Verification:**
  - `uv run python manage.py test` passed 133/133 tests; `uv run ruff check .` and `uv run ruff format --check .` passed cleanly.

---

## 🔮 Planned / Upcoming Features

- [x] **User Registration / Sign Up Flow:** Form with password validation and unique email verification.
- [x] **Password Reset / Recovery Flow:** Email-based token recovery workflow.
- [x] **User Profile Management:** Edit personal info, upload avatar image, update phone number.
- [x] **Product Catalog & Category Navigation:** Product models, categories, inventory tracking, search, and filtering.
- [x] **Shopping Cart & Checkout:** Persistent cart session, line item management, and order placement.
- [x] **Orders & Customer Portal:** Atomic inventory reduction, order management, and printable invoices.
- [x] **Enterprise Security Hardening & Defenses:** Headers (CSP, Referrer, Permissions), upload sanitization, HSTS, secure cookies.
- [x] **GitOps Automation & CI/CD:** GitHub Actions workflows, pre-commit hooks, Conventional Commits, SemVer changelog.
- [x] **Payment Gateway Integration:** Secure payment provider integration (Stripe & Card sandbox).
- [x] **Promotions & Coupon Discounts:** Coupon codes with percentage or fixed discount, minimum spend, and usage limits.
- [x] **Product Reviews & Star Ratings:** 1–5 star reviews with verified buyer badges and rating distributions.
- [x] **Customer Wishlist:** Save items for later with AJAX toggle and dedicated portal.
- [x] **Customer Address Book:** Stored addresses with 1-click checkout auto-fill.
- [x] **Order Cancellation & Stock Replenishment:** Cancel pending orders with atomic stock restoration.
- [x] **Transactional Emails:** Itemized HTML & plaintext confirmation receipts.
- [x] **Database Seeding Tool:** Single command `seed_db` for instant development setup.
- [ ] **Multi-Currency & Internationalization:** Dynamic currency switching and localization.
- [ ] **Real-Time Order Tracking & Shipment Webhooks:** Carrier integration for live tracking updates.
