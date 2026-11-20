---
trigger: always_on
description: Mandatory rule to automatically update FEATURE.md and README.md whenever a feature is implemented.
---

# Automatic Feature & README Synchronization Protocol

1. **Automatic Documentation in FEATURE.md:**
   - After successfully implementing and testing any feature or enhancement in this project, you must automatically log it in `FEATURE.md`.
   - Never wait for the user to ask for this.

2. **Automatic Synchronization of README.md:**
   - If the feature introduces new user-facing functionality, commands, configuration variables, or architecture changes, update `README.md` immediately in the same turn.

3. **Verification Prerequisite:**
   - Always run the relevant test suites (`uv run python manage.py test apps.<app>`) and linter (`uv run ruff check .`) before documenting the feature as complete.
   - Comply with `DESIGN_SYSTEM.md` on all frontend additions.
