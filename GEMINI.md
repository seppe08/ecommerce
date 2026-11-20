# Project Guidelines & Autonomous Documentation Rules for AuraStore

> **Scope:** Entire `ecommerce` repository across all AI agent sessions, chats, and tasks.  
> **Rule Type:** Always Active / Mandatory.

---

## 1. Mandatory Automatic Feature Tracking Protocol

Whenever any feature, module, enhancement, or major bug fix is successfully implemented and verified in this project:

1. **Autonomous `FEATURE.md` Updates (Mandatory):**
   - You MUST immediately and automatically document the new feature in `FEATURE.md`.
   - Do NOT wait for the user to ask or prompt you to update `FEATURE.md`.
   - Add the feature under the appropriate category or create a new section if needed.
   - Include:
     - **Feature Name & Category**
     - **Status** (Completed)
     - **Date of Completion**
     - **Technical Description** (what was built, behavior, design choices)
     - **Key Files Modified or Created**
     - **Verification / Test Coverage** details.

2. **Autonomous `README.md` Synchronization (Mandatory):**
   - In tandem with `FEATURE.md`, you MUST check and update `README.md` if the implemented feature affects:
     - Project capabilities, features overview, or tech stack.
     - New dependencies, environment variables (`.env.example`), or configuration steps.
     - New database tables, models, or migrations.
     - New commands, routes, views, endpoints, or testing instructions.
   - Do NOT wait for the user to ask or prompt you to update `README.md`.

3. **Autonomous Verification Before Documentation:**
   - Before listing a feature as completed in `FEATURE.md` and `README.md`, ensure it is properly verified:
     - Run automated tests (`uv run python manage.py test apps.<app_name>`).
     - Run the linter (`uv run ruff check .`).
     - Ensure no breaking changes or syntax errors.

---

## 2. Design System & UI/UX Constitution Enforcement

- Every frontend template, CSS style, or JavaScript interaction created in this project MUST comply with `DESIGN_SYSTEM.md`.
- Ensure zero Flash of Unstyled Content (FOUC).
- Maintain WCAG 2.1 AA accessibility standards (touch targets ≥ 44×44px, `:focus-visible` rings, ARIA labels).
- Test that every UI component renders flawlessly in both Light and Dark themes.

---

## 3. Python & Code Quality Standards

- Use `uv` for package management and tool execution (`uv run python manage.py ...`, `uv run ruff ...`).
- Adhere to Ruff linting rules (`uv run ruff check .`).
- All models extending `AbstractUser` or dealing with authentication must support unique emails and dual-identifier login where applicable.
