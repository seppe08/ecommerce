# Contributing to AuraStore

Thank you for your interest in contributing to **AuraStore**! We are committed to building an accessible, high-performance, and portfolio-grade e-commerce platform.

This guide outlines our standards, workflows, and best practices to ensure smooth collaboration and maintain exceptional codebase quality.

---

## 📑 Table of Contents

1. [Development Environment Setup](#-development-environment-setup)
2. [Git Branching Strategy](#-git-branching-strategy)
3. [Conventional Commits Standard](#-conventional-commits-standard)
4. [Code Quality & Pre-commit Hooks](#-code-quality--pre-commit-hooks)
5. [Design System & Accessibility Standards](#-design-system--accessibility-standards)
6. [Pull Request & Review Workflow](#-pull-request--review-workflow)
7. [Autonomous Documentation Protocol](#-autonomous-documentation-protocol)

---

## 🛠️ Development Environment Setup

AuraStore requires **Python 3.12+** and uses **[uv](https://github.com/astral-sh/uv)** as its high-speed package and project manager.

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/aurastore.git
cd aurastore
```

### 2. Configure Environment Variables
Copy the example environment configuration:
```bash
cp .env.example .env
```
*(On Windows PowerShell: `Copy-Item .env.example .env`)*

### 3. Install Dependencies with `uv`
```bash
uv sync
```

### 4. Apply Database Migrations
```bash
uv run python manage.py migrate
```

### 5. Install Pre-commit Hooks
```bash
uv run pre-commit install
```

### 6. Start the Development Server
```bash
uv run python manage.py runserver
```
Visit `http://127.0.0.1:8000` in your browser.

---

## 🌿 Git Branching Strategy

We follow a structured branch naming convention based on the type of work being performed:

| Branch Prefix | Purpose | Example |
| :--- | :--- | :--- |
| `feature/` | New user-facing capability or module | `feature/cart-checkout` |
| `fix/` | Bug fix or patch | `fix/avatar-upload-boundary` |
| `chore/` | Tooling, dependencies, or CI/CD updates | `chore/upgrade-ruff` |
| `docs/` | Documentation additions or updates | `docs/api-specification` |
| `refactor/` | Structural code improvements without changing behavior | `refactor/cart-session-helpers` |
| `perf/` | Performance optimizations | `perf/catalog-query-indexing` |

### Branch Flow
- **`main`**: Production-ready, stable releases.
- **`dev`**: Main development and integration branch.
- Feature branches branch off from `dev` and merge back into `dev` via Pull Requests.

---

## 📝 Conventional Commits Standard

All commits in AuraStore must strictly follow the **[Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)** specification.

### Commit Format
```text
<type>(<optional-scope>): <description>

[optional body]

[optional footer(s)]
```

### Supported Commit Types

- **`feat`**: A new feature or user-facing functionality.
  - *Example:* `feat(catalog): implement category filtering and search`
- **`fix`**: A bug fix or defect resolution.
  - *Example:* `fix(auth): prevent timing attacks during credential verification`
- **`docs`**: Documentation changes only.
  - *Example:* `docs: update CONTRIBUTING.md with branch conventions`
- **`style`**: Changes that do not affect code logic (formatting, whitespace, semi-colons).
  - *Example:* `style: format template whitespace in product_detail.html`
- **`refactor`**: Code changes that neither fix a bug nor add a feature.
  - *Example:* `refactor(accounts): extract profile validation into dedicated cleaner`
- **`perf`**: Code changes that improve runtime performance or query efficiency.
  - *Example:* `perf(catalog): add database index on product slug and sku`
- **`test`**: Adding missing tests or correcting existing test suites.
  - *Example:* `test(catalog): add unit tests for product stock availability property`
- **`chore`**: Changes to configuration, build pipeline, dependencies, or git hooks.
  - *Example:* `chore(deps): bump ruff to 0.9.9`

### Guidelines
1. Use the **imperative mood** in the description: *"add feature"* rather than *"added feature"*.
2. Do **not** capitalize the first letter of the description.
3. Do **not** place a period (`.`) at the end of the commit summary.
4. For breaking changes, append an exclamation mark after the type/scope (e.g., `feat(api)!: migrate auth token format`) and include `BREAKING CHANGE:` in the commit footer.

---

## 🔍 Code Quality & Pre-commit Hooks

Before pushing changes, ensure your code satisfies all quality gates.

### 1. Pre-commit Hooks
The repository includes automated pre-commit hooks configured in `.pre-commit-config.yaml`:
```bash
uv run pre-commit run --all-files
```
This runs:
- Ruff linter with auto-fix (`ruff --fix`)
- Ruff formatter (`ruff-format`)
- Whitespace and end-of-file fixers
- YAML syntax verification
- Merge conflict detector
- Private key and secret detector

### 2. Manual Linting & Formatting
```bash
# Lint checks
uv run ruff check .

# Auto-fix linting issues
uv run ruff check --fix .

# Code formatting check
uv run ruff format --check .

# Apply code formatting
uv run ruff format .
```

### 3. Automated Test Suite
All unit and integration tests must pass before opening a PR:
```bash
# Run entire test suite
uv run python manage.py test

# Run specific app tests
uv run python manage.py test apps.accounts
uv run python manage.py test apps.catalog
```

### 4. Deployment Security Check
Verify Django deployment configuration settings:
```bash
uv run python manage.py check --deploy
```

---

## 🎨 Design System & Accessibility Standards

Every frontend contribution must strictly comply with **`DESIGN_SYSTEM.md`**:

1. **Light & Dark Mode Support:** Every component, card, button, and input must render cleanly in both light and dark themes using CSS variables from `theme.css`.
2. **Zero-FOUC:** Ensure theme resolution script remains blocking in `<head>` so no unstyled flash occurs on page load.
3. **WCAG 2.1 AA Compliance:**
   - Interactive elements (buttons, inputs, links, chips) must have minimum touch targets of **44×44px**.
   - Keyboard navigation must display clear `:focus-visible` focus rings.
   - Use semantic HTML tags (`<nav aria-label="...">`, `<main>`, `<form role="search">`, etc.).
   - All forms must feature clear error states linked via `aria-describedby` and `aria-invalid`.

---

## 🚀 Pull Request & Review Workflow

1. **Create Branch:** Create a branch from `dev` following the branching convention (`feature/my-feature`).
2. **Implement & Test:** Write clean, modular code with accompanying unit/integration tests.
3. **Run Quality Checks:** Ensure `ruff check`, `ruff format`, `python manage.py test`, and pre-commit hooks pass with zero errors.
4. **Autonomous Documentation:** Synchronize `FEATURE.md` and `README.md` (see below).
5. **Open Pull Request:** Target the `dev` branch. Fill out all sections of `.github/PULL_REQUEST_TEMPLATE.md`.
6. **Continuous Integration (CI):** Ensure all GitHub Actions checks (Linting, Test Suite, Security Audit) pass.
7. **Code Review:** Address feedback from maintainers and peers. Once approved, pull requests are squash-merged or rebased into `dev`.

---

## 📖 Autonomous Documentation Protocol

To maintain complete and accurate documentation across iterations:
- **`FEATURE.md`:** Every completed and verified feature must be immediately recorded under the appropriate section with date, technical description, key files, and test coverage.
- **`README.md`:** Any changes affecting public architecture, models, routes, environment variables, or setup instructions must be updated in tandem.
- **`CHANGELOG.md`:** Document notable changes under the `[Unreleased]` section following the Keep a Changelog standard.
