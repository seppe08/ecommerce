# Changelog

All notable changes to the **AuraStore** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- **GitOps Automation & Pre-commit Hooks:**
  - Added `.pre-commit-config.yaml` configured with Astral Ruff (lint and format), `check-yaml`, `end-of-file-fixer`, `trailing-whitespace`, `check-merge-conflict`, and `detect-private-key`.
- **CI/CD GitHub Actions Workflows:**
  - Added `.github/workflows/ci.yml`: Multi-step continuous integration testing pipeline running Ruff linting, formatting check, Django test suite on Python 3.12 with `uv` caching, and deployment security check (`manage.py check --deploy`).
  - Added `.github/workflows/security.yml`: Automated security audit workflow running `pip-audit` for dependency vulnerability scanning and TruffleHog for secret scanning.
- **Developer Workflow & Templates:**
  - Added `.github/PULL_REQUEST_TEMPLATE.md` with comprehensive pre-merge checklist, change summary, and verification evidence sections.
  - Added `.github/ISSUE_TEMPLATE/feature_request.md` for structured feature proposals and design system alignment.
  - Added `.github/ISSUE_TEMPLATE/bug_report.md` for reproducible defect reporting across environments.
- **Contribution & Git Guidelines:**
  - Added `CONTRIBUTING.md` outlining the Conventional Commits standard (`feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `perf:`, `test:`, `chore:`), Git branch naming (`feature/*`, `fix/*`, `chore/*`), local setup with `uv`, pre-commit verification, and PR review workflow.
- **Security Hardening (In Progress):**
  - Production-ready security headers (HSTS, SSL redirect, secure session and CSRF cookies, X-Frame-Options, Content-Security-Policy).
  - Profile avatar upload sanitization, format verification with PIL, and 5MB size limit.

### Planned
- Shopping Cart with persistent session storage and line item management.
- Multi-step checkout pipeline with address capture and order placement.
- Stripe payment gateway integration with webhook event handling.

---

## [0.2.0] - 2026-11-21

### Milestone: Product Catalog & Categories

### Added
- **Catalog Data Models:**
  - `Category` model with unique slug, description, image, and active toggle.
  - `Product` model with pricing, stock counter, SKU uniqueness, indexed slugs, and category foreign key.
  - `ProductImage` model supporting multi-image galleries with designated primary image and fallback logic.
  - Dynamic inventory stock evaluation property `Product.is_in_stock`.
- **Views & User Experience:**
  - Product catalog list view (`/products/`) with dual category filtering (URL slug & query param), full-text search across title, description, and SKU, sorting (price asc/desc, newest, name A-Z), active category chips, and pagination (12 items/page).
  - Product detail showcase (`/products/<slug>/`) featuring interactive thumbnail switcher, stock status badges, specifications table, quantity selector, and related products grid.
- **Django Admin Customization:**
  - `CategoryAdmin` with dynamically annotated product counts, active status filters, and slug auto-population.
  - `ProductAdmin` with tabular `ProductImageInline`, search by SKU/name, and list-editable price/stock fields.
- **Accessibility & Design:**
  - Strict compliance with `DESIGN_SYSTEM.md` and WCAG 2.1 AA standards (minimum 44×44px touch targets, `:focus-visible` rings, semantic markup).
- **Automated Test Coverage:**
  - Comprehensive 23-case test suite in `apps/catalog/tests.py` testing model constraints, stock properties, admin configurations, search, filtering, sorting, pagination, and detail views.

---

## [0.1.0] - 2026-11-20

### Milestone: Authentication & Design System

### Added
- **Core Architecture & Tooling:**
  - Modern Python 3.12+ and Django 6.1+ foundation with Astral `uv` package management and PostgreSQL 18 compatibility via Docker Compose.
  - Twelve-factor environment configuration using `django-environ`.
- **Custom User Model & Authentication:**
  - `apps.accounts.models.CustomUser` extending `AbstractUser` with unique email requirement and profile fields (`phone`, `birth_date`, `profile_picture`).
  - Dual-identifier authentication backend (`EmailOrUsernameModelBackend`) supporting interchangeable, case-insensitive login with username or email, hardened with timing attack defense.
  - Custom login form (`CustomLoginForm`) with empathetic error handling and 30-day "Remember Me" session persistence.
  - Full user registration flow (`RegisterView`, `CustomRegistrationForm`) with password confirmation and automatic post-registration login.
  - User profile management dashboard (`ProfileView`, `UserProfileForm`) for updating personal info and uploading avatars.
  - 4-step secure password reset and recovery workflow using email tokens (`CustomPasswordResetView`, `CustomPasswordResetConfirmView`).
  - Custom logout view with clean session termination and CSRF protection.
- **Design System & Frontend Architecture:**
  - Zero-FOUC Dark and Light theme engine implemented with CSS variables and synchronous theme resolution in `<head>`.
  - Accessible UI components with WCAG 2.1 AA minimum 44×44px touch targets and high-empathy inline error feedback.
- **Automated Test Coverage:**
  - Comprehensive 30-case test suite in `apps/accounts/tests.py` verifying all authentication, registration, profile, password reset, and backend flows.
