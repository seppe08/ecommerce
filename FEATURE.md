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

## 🔮 Planned / Upcoming Features

- [x] **User Registration / Sign Up Flow:** Form with password validation and unique email verification.
- [x] **Password Reset / Recovery Flow:** Email-based token recovery workflow.
- [x] **User Profile Management:** Edit personal info, upload avatar image, update phone number.
- [x] **Product Catalog & Category Navigation:** Product models, categories, inventory tracking, search, and filtering.
- [x] **Shopping Cart & Checkout:** Persistent cart session, line item management, and order placement.
- [ ] **Payment Gateway Integration:** Secure payment provider integration (e.g., Stripe).
