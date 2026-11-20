# AuraStore — Modern E-Commerce Platform

A production-grade, highly accessible, and visually stunning e-commerce web platform built with **Python 3.12+**, **Django 6.1+**, **uv**, and **PostgreSQL**. AuraStore is engineered with a strict UI/UX design constitution, modern theme tokens (zero-FOUC dark/light mode), robust authentication, and comprehensive test coverage.

---

## 🌟 Key Highlights

- **Dual-Identifier Authentication:** Log in seamlessly using either your unique **Username** or verified **Email** address (case-insensitive).
- **User Registration Flow:** Sign up with unique username/email validation, password policy confirmation, and automatic session login.
- **User Profile Management:** Authenticated profile dashboard supporting first/last name, phone, date of birth, and avatar image uploads.
- **Password Reset & Recovery:** Full 4-step secure password recovery workflow via email tokens, custom forms, and accessible reset views.
- **Zero-FOUC Dark & Light Modes:** Synchronous theme resolution in `<head>` prevents any flash of unstyled color; persists preferences via `localStorage` with OS-level fallback.
- **Enterprise-Grade Security:** Timing attack resistance, open-redirect mitigation, granular error handling without credential leaking, and safe session expiration handling.
- **Session Flexibility:** 30-day persistent session support via "Remember Me", or secure browser-close expiry.
- **High-Empathy UI/UX:** Inline field-anchored errors, live loading spinner states on submission to prevent double clicks, and accessible password visibility toggles.
- **WCAG 2.1 AA Accessibility:** Minimum 44×44px interactive touch targets, visible keyboard focus rings (`:focus-visible`), skip-to-content links, and full ARIA semantics.
- **100% Automated Test Suite:** 30 comprehensive unit and integration tests covering the complete authentication, registration, profile, and security lifecycle.

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
| **Linter / Formatter**| `Ruff` | `>= 0.17.5` | Fast Python linter & code formatter |

---

## 📁 Repository Structure

```text
ecommerce/
├── apps/
│   └── accounts/               # Custom user management & authentication app
│       ├── migrations/         # Database migration files
│       ├── admin.py            # CustomUser admin configuration
│       ├── apps.py             # App configuration
│       ├── backends.py         # EmailOrUsernameModelBackend (dual auth)
│       ├── forms.py            # CustomLoginForm, CustomRegistrationForm, UserProfileForm, CustomPasswordResetForm, CustomSetPasswordForm
│       ├── models.py           # CustomUser model (AbstractUser)
│       ├── tests.py            # Comprehensive 30-case test suite
│       ├── urls.py             # App URL patterns (login, logout, register, profile, password reset)
│       └── views.py            # CustomLoginView, CustomLogoutView, RegisterView, ProfileView, HomeView, Password Reset Views
├── core/
│   ├── asgi.py                 # ASGI configuration
│   ├── settings.py             # Django project settings & database configuration
│   ├── urls.py                 # Root URL router
│   └── wsgi.py                 # WSGI application entrypoint
├── static/
│   ├── css/
│   │   └── theme.css           # Design tokens, variables & full component styles
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
│   ├── base.html               # Master layout with zero-FOUC theme script & header
│   └── home.html               # Dashboard & catalog showcase view
├── .env.example                # Template for environment configuration
├── .gitignore                  # Production Git ignore patterns
├── DESIGN_SYSTEM.md            # Single source of truth for UI/UX & typography standards
├── docker-compose.yaml         # PostgreSQL 18 container configuration
├── FEATURE.md                  # Chronological inventory of implemented features
├── GEMINI.md                   # Workspace agent guidelines & mandatory update protocols
├── manage.py                   # Django CLI utility
├── pyproject.toml              # Project dependencies & tool configurations
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
```

### 3. Install Dependencies
Install dependencies with `uv`:
```bash
uv sync
```

### 4. Database Setup

#### Option A: PostgreSQL via Docker Compose
To start a containerized PostgreSQL 18 instance:
```bash
docker compose up -d
```

#### Option B: SQLite (Quick Local Development)
Set `DB_ENGINE=django.db.backends.sqlite3` in your `.env` file.

### 5. Run Migrations & Create Superuser
Apply migrations to initialize the database schema:
```bash
uv run python manage.py migrate
```

Create a superuser to access the Django administration panel:
```bash
uv run python manage.py createsuperuser
```

### 6. Start Development Server
```bash
uv run python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## 🧪 Running Automated Tests & Linting

### Running Unit & Integration Tests
Execute the comprehensive test suite in `apps/accounts/tests.py`:
```bash
uv run python manage.py test apps.accounts
```
*All 30 authentication, registration, profile management, password recovery, and security test cases will execute.*

### Code Quality & Linter
Run `Ruff` to verify code standards:
```bash
# Check code style and lint rules
uv run ruff check .

# Automatically apply safe fixes
uv run ruff check --fix .
```

---

## 🎨 UI/UX Design System & Constitution

All frontend components strictly adhere to [DESIGN_SYSTEM.md](file:///c:/Users/seppe/Projects/ecommerce/DESIGN_SYSTEM.md).

- **Typography:** Built on **Plus Jakarta Sans** with a typographic scale from `display-1` (36px, weight 800) to `micro-badge` (12px, weight 700).
- **Themes:** Semantic CSS custom properties mapped to light and dark palettes.
- **Transitions:** Standardized cubic transitions (150ms–220ms) for tactile feel.
- **Touch & Accessibility:** Strict adherence to WCAG 2.1 AA standards.

---

## 📜 Continuous Feature & Documentation Protocol

This repository adheres to an autonomous documentation workflow enforced via [GEMINI.md](file:///c:/Users/seppe/Projects/ecommerce/GEMINI.md):
- **Feature Tracking:** Every feature successfully implemented is immediately logged in [FEATURE.md](file:///c:/Users/seppe/Projects/ecommerce/FEATURE.md).
- **README Updates:** Whenever a new feature alters setup instructions, endpoints, or platform capabilities, this `README.md` is updated automatically in the same turn without requiring explicit user instruction.
