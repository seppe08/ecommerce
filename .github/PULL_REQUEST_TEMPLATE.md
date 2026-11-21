## 📌 Summary of Changes

<!-- Briefly describe the purpose and context of this pull request. What problem does it solve? -->

---

## 🏷️ Type of Change

- [ ] `feat`: New feature or capability
- [ ] `fix`: Bug fix
- [ ] `docs`: Documentation updates
- [ ] `style`: Formatting, missing semi-colons, no code logic changes
- [ ] `refactor`: Refactoring code without altering functionality
- [ ] `perf`: Performance optimization
- [ ] `test`: Adding or correcting tests
- [ ] `chore`: Tooling, CI/CD, dependency updates, or gitops

---

## 📋 Pre-Merge Checklist

- [ ] My code adheres to the project's code quality and styling standards (`uv run ruff check .` and `uv run ruff format --check .`).
- [ ] Comprehensive unit and integration tests are included or updated.
- [ ] The full automated test suite passes cleanly (`uv run python manage.py test`).
- [ ] Deployment security checks pass without unexpected errors (`uv run python manage.py check --deploy`).
- [ ] If new features or capabilities are introduced, **`FEATURE.md`** has been automatically updated in compliance with project rules.
- [ ] If user-facing changes, models, environment variables, or commands were added, **`README.md`** has been synchronized.
- [ ] All UI changes strictly comply with **`DESIGN_SYSTEM.md`** (Light/Dark mode, zero-FOUC, WCAG 2.1 AA touch targets >= 44x44px).
- [ ] No secrets, credentials, or sensitive environment variables are committed.

---

## 🧪 Verification & Testing Evidence

<!-- Please paste the execution output from the tests and linter, or attach screenshots/screen recordings for UI changes. -->

```bash
uv run ruff check .
uv run python manage.py test
uv run python manage.py check --deploy
```

**Results / Output:**
```text
<!-- Paste output here -->
```

---

## 🔗 Related Issues & Pull Requests

<!-- Closes #123, Relates to #456 -->
- Resolves: 
