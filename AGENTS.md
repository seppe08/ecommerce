# Autonomous Feature & Documentation Synchronization Rules

> **Scope:** Entire `ecommerce` workspace across all agent sessions and conversations.  
> **Rule Type:** Always Active / Mandatory.

## 1. Automatic Feature Documentation (`FEATURE.md`)
- Whenever any feature, capability, or major enhancement is successfully implemented and tested in this project, you MUST automatically document it in `FEATURE.md` without requiring the user to ask.
- Keep `FEATURE.md` structured with: Feature name, completion date, technical description, key files created/modified, and verification status.

## 2. Automatic Project Documentation (`README.md`)
- Concurrently update `README.md` whenever the newly added feature introduces new endpoints, environment configurations, models, dependencies, or user-facing functionality.
- Never wait for user reminders to keep `README.md` synchronized.

## 3. Mandatory Quality Checks Before Sign-off
- Verify the feature with `uv run python manage.py test apps.<app>` and `uv run ruff check .`.
- Confirm strict adherence to `DESIGN_SYSTEM.md` for any UI components (Light/Dark themes, accessibility, zero-FOUC).
