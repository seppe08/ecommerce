# Project Guidelines & Autonomous Documentation Rules (AuraStore)

> **Scope:** Entire `ecommerce` repository across all AI agent sessions, chats, and tasks.
> **Rule Type:** Always Active / Mandatory.

---

## 1. Automatic Feature & Project Documentation

Whenever any feature, capability, enhancement, or major bug fix is successfully implemented and verified:

1. **Update `FEATURE.md` (Mandatory):**
   - Immediately and automatically document the new feature in `FEATURE.md` without waiting for the user to ask.
   - Include: Feature Name & Category, Status (`Completed`), Date of Completion, Technical Description, Key Files Created/Modified, and Verification / Test Coverage.

2. **Synchronize `README.md` (Mandatory):**
   - Concurrently update `README.md` whenever the change introduces new endpoints, environment variables (`.env.example`), models, migrations, commands, dependencies, or user-facing functionality.

3. **Update `CHANGELOG.md`:**
   - Record notable user-facing or architectural changes under `[Unreleased]` following Keep a Changelog.

---

## 2. Mandatory Quality Checks Before Sign-off

- Run automated tests: `uv run python manage.py test` (or `uv run python manage.py test apps.<app>`).
- Run the linter and formatter check: `uv run ruff check .` and `uv run ruff format --check .`.
- Run deployment check when settings/security change: `uv run python manage.py check --deploy`.

---

## 3. Design System & Code Quality Standards

- **UI/UX Constitution:** Every frontend template, CSS style, or JS interaction MUST strictly comply with `DESIGN_SYSTEM.md` (Light/Dark themes, zero-FOUC, WCAG 2.1 AA touch targets ≥ 44×44px, `:focus-visible` rings, ARIA labels).
- **Tooling:** Use `uv` for Python package management and execution (`uv run python manage.py ...`, `uv run ruff ...`).
- **Authentication Models:** Models extending `AbstractUser` or handling authentication must support unique emails and dual-identifier login where applicable.
