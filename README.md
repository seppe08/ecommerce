# AuraStore — Modern E-Commerce Platform

A production-grade, highly accessible, and visually stunning e-commerce web platform built with **Python 3.12+**, **Django 6.1+**, **uv**, and **PostgreSQL**. AuraStore is engineered with a strict UI/UX design constitution, modern theme tokens (zero-FOUC dark/light mode), robust authentication, and comprehensive test coverage.

---

## 🌟 Key Highlights

- **Calm, Editorial Storefront UI/UX:** Premium, neutral-first retail experience putting product photography first. Loaded Google Fonts `Fraunces` serif alongside `Plus Jakarta Sans`, fluid typography scaling with `clamp()`, 4:5 image aspect ratios, secondary hover image crossfade, and AJAX quick-add actions.
- **Product Catalog & Category Exploration:** Browse comprehensive product offerings with real-time category filtering, SKU and keyword search, sorting (price, newest, name), horizontally scrollable chips with scroll-snap on mobile, and designed empty states.
- **Rich Multi-Image Gallery Showcase:** Interactive product detail views with pure CSS click-to-zoom (`scale(1.6)`), multi-image thumbnail switcher, sticky gallery and sticky buy box with quantity stepper, tabbed specifications, and related product rail.
- **Session-Backed Shopping Cart Engine:** Fast, zero-database-overhead cart persistence supporting item quantities, line totals, stock boundary clamping, and dynamic cart counter bump animations.
- **Multi-Step Checkout & Stepper Flow:** Streamlined checkout with a 3-step progress stepper (`Cart → Checkout → Confirmation`), responsive 2-column layout, sticky order summary on desktop, and collapsible summary toggle on mobile.
- **Atomic Checkout & Inventory Management:** Concurrency-safe checkout with `select_for_update()` product locking, atomic inventory decrements, and automatic rollback on stock insufficiency.
- **Customer Portal & Invoice Receipts:** Customer order history dashboard (`/orders/my-orders/`), status filtering, and print-ready invoices (`@media print`) rendering `#000000` text with zero backgrounds.
- **Dual-Identifier Authentication:** Log in seamlessly using either your unique **Username** or verified **Email** address (case-insensitive).
- **User Registration Flow:** Sign up with unique username/email validation, password policy confirmation, and automatic session login.
- **User Profile Management:** Authenticated profile dashboard supporting first/last name, phone, date of birth, and avatar image uploads.
- **Password Reset & Recovery:** Full 4-step secure password recovery workflow via email tokens, custom forms, and accessible reset views.
- **Zero-FOUC Dark & Light Modes:** Synchronous theme resolution in `<head>` prevents any flash of unstyled color; persists preferences via `localStorage` with OS-level fallback.
- **Enterprise-Grade Security Hardening:** Comprehensive defense-in-depth including environment-controlled HSTS, secure cookies (`HttpOnly`, `SameSite=Lax`, `Secure`), Content-Security-Policy (CSP), `Referrer-Policy`, `Permissions-Policy`, clickjacking defense (`DENY`), avatar file upload boundaries (5MB limit, JPEG/PNG/WebP format & PIL header verification), and strict open-redirect mitigation.
- **Session Flexibility:** 30-day persistent session support via "Remember Me", or secure browser-close expiry.
- **High-Empathy UI/UX:** Inline field-anchored errors, live loading spinner states on submission to prevent double clicks, and accessible password visibility toggles.
- **WCAG 2.1 AA Accessibility:** Minimum 44×44px interactive touch targets, visible keyboard focus rings (`:focus-visible`), skip-to-content links, and full ARIA semantics.
- **Stripe & Card Payment Gateway:** Full checkout payment integration supporting Credit / Debit cards via Stripe with sandbox test card simulation, decline handling, Cash on Delivery option, and webhook processing.
- **Promotions & Coupon Discounts:** High-flexibility discount engine supporting percentage-off and fixed-dollar coupons, date windows, minimum order spend, usage caps, and real-time cart redemption.
- **Product Reviews & Customer Ratings:** 1–5 star customer reviews with verified buyer badges, average rating metrics, and distribution progress bars.
- **Customer Wishlist & Saved Items:** Saved items portal (`/products/wishlist/`) with instantaneous AJAX heart toggle and "Move to Cart" actions.
- **Saved Customer Address Book:** Customer address book with default address auto-filling during checkout and 1-click address selector chips.
- **Order Cancellation & Stock Restoration:** Self-service order cancellation for pending orders with concurrency-safe inventory replenishment.
- **Transactional Confirmation Emails:** Itemized HTML & plaintext order confirmation receipts automatically dispatched upon purchase.
- **Database Seeder (`python manage.py seed_db`):** One-command database population with curated categories, products, reviews, coupons, and a demo account.
- **100% Automated Test Suite:** 133 comprehensive unit, integration, and security tests covering authentication, registration, profile management, password recovery, product catalog, categories, gallery, shopping cart, atomic checkout, customer invoicing, security headers, file upload boundaries, open-redirect defenses, Stripe payments, coupons, reviews, wishlists, order cancellation, and emails.
- **GitOps & CI/CD Automation:** Robust multi-step GitHub Actions CI pipelines (Ruff linting & formatting, Python 3.12 Django testing with `uv` caching, and deployment security audits), automated `pip-audit` and secret scanning, pre-commit hooks, Conventional Commits, and SemVer changelog.

---

## 🛠️ Technology Stack

| Component | Technology | Version | Description |
| :--- | :--- | :--- | :--- |
| **Language** | Python | `>= 3.12` | Modern Python features & type support |
| **Framework** | Django | `>= 6.1.3` | High-level Python web framework |
| **Package Manager**| `uv` | Latest | High-performance Python package & project manager |
| **Database** | PostgreSQL / SQLite | `18` (Postgres) | Production PostgreSQL via Docker Compose or SQLite for local dev |
| **Configuration** | `django-environ` | `>= 0.14.0` | Twelve-factor configuration via `.env` |
| **Image Processing**| `Pillow` | `>= 13.0.0` | Profile and product media processing |
| **Database Driver** | `psycopg[binary]` | `>= 3.3.9` | High-efficiency PostgreSQL adapter |
| **Payments** | `stripe` | `>= 17.1.0` | Payment gateway and webhook handling |
| **Linter / Formatter**| `Ruff` | `>= 0.17.5` | Fast Python linter & code formatter |
| **Frontend Styling**| `Tailwind CSS v4` | `^4.0.0` | Utility CSS & token architecture via `@tailwindcss/cli` |


---

## 📁 Repository Structure

```text
ecommerce/
├── .github/                    # GitHub Actions workflows and issue/PR templates
│   ├── ISSUE_TEMPLATE/         # Bug report and feature request issue templates
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   ├── workflows/              # CI/CD and security audit automation
│   │   ├── ci.yml              # Ruff linting, test suite & deploy check
│   │   └── security.yml        # pip-audit vulnerability & secret scanning
│   └── PULL_REQUEST_TEMPLATE.md# Pre-merge checklist & verification template
├── apps/
│   ├── accounts/               # Custom user management & authentication app
│   │   ├── migrations/         # Database migration files (CustomUser & Address)
│   │   ├── admin.py            # CustomUser & Address admin configuration
│   │   ├── apps.py             # App configuration
│   │   ├── backends.py         # EmailOrUsernameModelBackend (dual auth)
│   │   ├── forms.py            # CustomLoginForm, CustomRegistrationForm, UserProfileForm, CustomPasswordResetForm, CustomSetPasswordForm
│   │   ├── models.py           # CustomUser (AbstractUser) & Address models
│   │   ├── tests.py            # Comprehensive 30-case accounts & auth test suite
│   │   ├── tests_security.py   # Comprehensive 23-case automated security test suite
│   │   ├── urls.py             # App URL patterns (login, logout, register, profile, password reset)
│   │   └── views.py            # CustomLoginView, CustomLogoutView, RegisterView, ProfileView, HomeView, Password Reset Views
│   ├── catalog/                # Product catalog, reviews & wishlist app
│   │   ├── management/         # Custom management commands (`seed_db`)
│   │   ├── migrations/         # Category, Product, ProductImage, Review & Wishlist migrations
│   │   ├── admin.py            # Admin configs with inlines & product counts
│   │   ├── apps.py             # Catalog app configuration
│   │   ├── forms.py            # ReviewForm for customer product reviews
│   │   ├── models.py           # Category, Product, ProductImage, Review & Wishlist models
│   │   ├── tests.py            # Comprehensive 29-case test suite
│   │   ├── urls.py             # Product list, category, detail, review & wishlist routes
│   │   └── views.py            # ProductListView, ProductDetailView, review & wishlist views
│   ├── cart/                   # Session-backed shopping cart & coupon engine app
│   │   ├── apps.py             # Cart app configuration
│   │   ├── cart.py             # Session engine managing item quantities, coupons & totals
│   │   ├── context_processors.py # Global cart context processor
│   │   ├── forms.py            # CartAddProductForm
│   │   ├── tests.py            # Comprehensive 23-case test suite
│   │   ├── urls.py             # Cart & coupon routes (detail, add, remove, update, coupon apply/remove)
│   │   └── views.py            # cart_detail, cart_add, cart_remove, cart_update_quantity, coupon views
│   └── orders/                 # Order management, Stripe payments & checkout app
│       ├── migrations/         # Order, OrderItem & Coupon migrations
│       ├── admin.py            # OrderAdmin & CouponAdmin with inline items and bulk actions
│       ├── apps.py             # Orders app configuration
│       ├── forms.py            # OrderCreateForm & CardPaymentForm
│       ├── models.py           # Order, OrderItem & Coupon models
│       ├── tests.py            # Comprehensive 28-case test suite
│       ├── urls.py             # Checkout, Stripe payment, webhook, cancel, list & invoice routes
│       └── views.py            # order_create, order_payment, stripe_webhook, order_cancel, order_created, order_list, order_detail
├── core/
│   ├── asgi.py                 # ASGI configuration
│   ├── middleware.py           # SecurityHeadersMiddleware (CSP, Referrer-Policy, Permissions-Policy)
│   ├── settings.py             # Django project settings & database configuration
│   ├── urls.py                 # Root URL router
│   └── wsgi.py                 # WSGI application entrypoint
├── static/
│   ├── css/
│   │   ├── tailwind/input.css  # Tailwind CSS v4 @theme & layer configuration
│   │   ├── app.css             # Compiled production CSS bundle
│   │   └── theme.css           # Design tokens, variables & legacy component styles
│   └── js/
│       └── theme.js            # Theme toggle, password visibility, form spinners
├── templates/
│   ├── accounts/
│   │   ├── login.html          # Split-screen responsive login template
│   │   ├── register.html       # Split-screen registration template
│   │   ├── profile.html        # User profile & avatar management template
│   │   ├── password_reset_form.html     # Password reset email submission
│   │   ├── password_reset_done.html     # Reset link dispatch notice
│   │   ├── password_reset_confirm.html  # New password setup with token verification
│   │   ├── password_reset_complete.html # Success confirmation screen
│   │   ├── password_reset_email.html    # HTML/text reset instructions
│   │   └── password_reset_subject.txt   # Reset email subject line
│   ├── catalog/
│   │   ├── product_list.html   # Product catalog with search, filters & pagination
│   │   ├── product_detail.html # Rich product view with gallery, reviews & related products
│   │   └── wishlist.html       # Customer saved items wishlist portal
│   ├── cart/
│   │   └── cart_detail.html    # Full cart breakdown, coupon redemption & summary
│   ├── includes/
│   │   └── product_card.html   # Unified Tailwind product card component
│   ├── orders/
│   │   ├── emails/
│   │   │   ├── order_confirmation.html # HTML order receipt email
│   │   │   └── order_confirmation.txt  # Plaintext order receipt email
│   │   ├── order_create.html   # Checkout form with saved addresses & sticky order breakdown
│   │   ├── order_payment.html  # Stripe card payment & sandbox test form
│   │   ├── order_created.html  # Order confirmation & receipt summary
│   │   ├── order_list.html     # My Orders customer portal with status filters
│   │   └── order_detail.html   # Detailed print-ready invoice & order cancellation
│   ├── base.html               # Master layout with zero-FOUC theme script & header
│   └── home.html               # Dashboard & catalog showcase view
├── .env.example                # Template for environment configuration
├── .gitignore                  # Production Git ignore patterns
├── .pre-commit-config.yaml     # Git pre-commit hooks (Ruff, YAML, secrets)
├── AGENTS.md                   # Workspace agent guidelines & mandatory update protocols
├── CHANGELOG.md                # SemVer release history following Keep a Changelog
├── CONTRIBUTING.md             # Developer guidelines, Conventional Commits & workflow
├── DESIGN_SYSTEM.md            # Single source of truth for UI/UX & typography standards
├── docker-compose.yaml         # PostgreSQL 18 container configuration
├── FEATURE.md                  # Chronological inventory of implemented features
├── manage.py                   # Django CLI utility
├── package.json                # Tailwind CSS v4 build scripts & devDependencies
├── package-lock.json           # Locked npm dependencies
├── pyproject.toml              # Project dependencies & tool configurations
├── SECURITY.md                 # Vulnerability disclosure process & defense architecture
└── uv.lock                     # Pinned deterministic dependency lockfile
```

---

## ⚡ Quickstart & Installation

Follow these steps to set up the project locally for development:

### 1. Prerequisites
- [Python 3.12+](https://www.python.org/)
- [`uv`](https://docs.astral.sh/uv/) package manager (`curl -LsSf https://astral.sh/uv/install.sh` or `winget install astral-sh.uv`)
- [Docker Desktop](https://www.docker.com/) (optional, if using PostgreSQL)

### 2. Clone & Environment Setup
Clone the repository and create your local environment file:
```bash
git clone <repository-url>
cd ecommerce

# Copy the example environment file
cp .env.example .env
```

Review `.env` and configure your settings:
```ini
SECRET_KEY=your-secure-random-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Select database engine:
# For SQLite:
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=ecommerce.sqlite3

# For PostgreSQL (via Docker or local instance):
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=ecommerce
# DB_USER=django
# DB_PASSWORD=your_password
# DB_HOST=localhost
# DB_PORT=5432

# Stripe Payment Gateway (sandbox test keys)
STRIPE_PUBLISHABLE_KEY=pk_test_aurastore_mock_key
STRIPE_SECRET_KEY=sk_test_aurastore_mock_key
STRIPE_WEBHOOK_SECRET=
```

### 3. Install Dependencies
Install Python dependencies with `uv`:
```bash
uv sync
```

### 3.1 Frontend Build Pipeline (Tailwind CSS v4)
Install frontend build devDependencies:
```bash
npm install
```

Compile the CSS bundle (`static/css/tailwind/input.css` → `static/css/app.css`):
```bash
npm run build:css
```

For real-time development watch mode:
```bash
npm run watch:css
```

> **Note on Deployments:** `static/css/app.css` is committed directly to source control. Production environments and deployment targets do not require Node.js or npm runtime dependencies—standard Python deployment commands (`collectstatic`) function out of the box.

### 4. Database Setup

#### Option A: PostgreSQL via Docker Compose
To start a containerized PostgreSQL 18 instance:
```bash
docker compose up -d
```

#### Option B: SQLite (Quick Local Development)
Set `DB_ENGINE=django.db.backends.sqlite3` in your `.env` file.

### 5. Run Migrations, Seed Sample Data & Create Superuser
Apply migrations to initialize the database schema:
```bash
uv run python manage.py migrate
```

Optionally populate curated categories, products, reviews, coupons (`WELCOME10`, `SAVE20`, `FLAT25`), and a demo customer account (`customer@aurastore.com` / `Password123!`):
```bash
uv run python manage.py seed_db
```

Create a superuser to access the Django administration panel:
```bash
uv run python manage.py createsuperuser
```

### 6. Install Pre-commit Hooks (Recommended)
```bash
uv run pre-commit install
```

### 7. Start Development Server
```bash
uv run python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## 🧪 Running Automated Tests & Linting

### Running Unit & Integration Tests
Execute the comprehensive test suites:
```bash
# Test the Shopping Cart and Orders & Checkout apps (51 test cases)
uv run python manage.py test apps.cart apps.orders

# Test the Product Catalog app (29 test cases)
uv run python manage.py test apps.catalog

# Test the Accounts & Auth app (53 test cases including security suite)
uv run python manage.py test apps.accounts

# Test the Security Hardening suite specifically (23 test cases)
uv run python manage.py test apps.accounts.tests_security

# Run all test suites across the project (133 test cases)
uv run python manage.py test
```
*All 133 unit, integration, and security tests across accounts, auth, catalog, cart, orders, and defensive controls will execute.*

### Deployment Security Verification
Check production deployment settings:
```bash
uv run python manage.py check --deploy
```

### Code Quality, Formatting & Pre-commit
Run `Ruff` and pre-commit checks:
```bash
# Check code style and lint rules
uv run ruff check .

# Automatically apply safe fixes
uv run ruff check --fix .

# Verify code formatting
uv run ruff format --check .

# Run all pre-commit hooks across all files
uv run pre-commit run --all-files
```

---

## 🤝 Contributing & Changelog

- **[CONTRIBUTING.md](CONTRIBUTING.md):** Guidelines on branch conventions, Conventional Commits standard (`feat:`, `fix:`, `docs:`, `chore:`), PR review workflows, and testing criteria.
- **[CHANGELOG.md](CHANGELOG.md):** Chronological milestone release notes adhering to Keep a Changelog and Semantic Versioning (v0.1.0, v0.2.0, and Unreleased).
- **Pull Request Template:** Standardized pre-merge verification checklist in `.github/PULL_REQUEST_TEMPLATE.md`.
- **Issue Templates:** Feature requests and bug reports in `.github/ISSUE_TEMPLATE/`.

---

## 🎨 UI/UX Design System & Constitution

All frontend templates and components strictly adhere to [DESIGN_SYSTEM.md](DESIGN_SYSTEM.md).

- **Calm, Product-First Aesthetic:** Neutral-first UI chrome (warm off-white `#FAF9F6` in light mode; warm charcoal `#0F1012` in dark mode) letting product photography shine without loud startup gradients. Single accent per mode (deep teal `#2B5B5F` in light; muted amber `#D8A65A` in dark).
- **Typography:** Refined editorial serif **Fraunces** for headlines and display alongside **Plus Jakarta Sans** for body and interface controls. Fluid scaling via CSS `clamp()` and tabular numerals for pricing.
- **Themes & Zero-FOUC:** Synchronous `<head>` theme resolution, zero flash of wrong theme, and smooth cross-fading mode toggle.
- **Product Showcase:** Strict 4:5 media aspect ratio, secondary gallery image crossfades on hover, and desktop/mobile quick-add interactions.
- **Touch & Accessibility:** WCAG 2.1 AA compliance across light and dark themes, touch targets ≥ 44×44px, `:focus-visible` rings, and full `prefers-reduced-motion` compliance.

---

## 📜 Continuous Feature & Documentation Protocol

This repository adheres to an autonomous documentation workflow enforced via [AGENTS.md](AGENTS.md):
- **Feature Tracking:** Every feature successfully implemented is immediately logged in [FEATURE.md](FEATURE.md).
- **README Updates:** Whenever a new feature alters setup instructions, endpoints, or platform capabilities, this `README.md` is updated automatically in the same turn without requiring explicit user instruction.
