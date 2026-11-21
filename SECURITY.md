# AuraStore Security Policy & Defenses

AuraStore is committed to maintaining the highest security and privacy standards for our users, customer data, and infrastructure. This document outlines our security policies, responsible vulnerability disclosure process, and the architectural defenses built directly into the platform.

---

## 🛡️ Supported Versions

Only the latest active release branch receives proactive security updates and patches:

| Version | Supported          | Status             |
| ------- | ------------------ | ------------------ |
| `main`  | :white_check_mark: | Actively supported |
| `< 1.0` | :x:                | End of Life        |

---

## 🚨 Reporting a Vulnerability (Responsible Disclosure)

If you discover or suspect a security vulnerability in AuraStore, please disclose it responsibly. **Do not create public GitHub issues or forum posts.**

### Disclosure Protocol
1. **Email:** Send your vulnerability details to `security@aurastore.internal` or open a private GitHub Security Advisory.
2. **Encrypted Communication:** Include a descriptive summary of the potential vulnerability, affected endpoints/components, and step-by-step reproduction instructions or a minimal Proof of Concept (PoC).
3. **Response SLA:**
   - **Acknowledgment:** Within 24 hours of submission.
   - **Initial Assessment & Triage:** Within 48 hours.
   - **Remediation & Patch Deployment:** Critical severity within 7 days; high/medium severity within 14–30 days.
4. **Coordinated Disclosure:** We request that you refrain from publicly discussing or disclosing the vulnerability until a patch has been released and verified.

---

## 🔒 Built-in Architectural Defenses

AuraStore incorporates defense-in-depth principles across transport, session management, HTTP headers, file handling, authentication, and database access.

### 1. Transport Layer Security & HSTS
- **HTTPS Enforcement:** `SECURE_SSL_REDIRECT` can be enabled via environment configuration (`SECURE_SSL_REDIRECT=True`), routing all unencrypted HTTP traffic to HTTPS.
- **HTTP Strict Transport Security (HSTS):** Enabled by default in production (`SECURE_HSTS_SECONDS=31536000`), with `SECURE_HSTS_INCLUDE_SUBDOMAINS=True` and `SECURE_HSTS_PRELOAD=True` to guarantee strict browser-level TLS enforcement.

### 2. Cookie Security & Session Hardening
- **Session Cookies:** Configured with `SESSION_COOKIE_HTTPONLY = True` (mitigating XSS session theft) and `SESSION_COOKIE_SAMESITE = 'Lax'` (mitigating cross-site request forgery). In production (`DEBUG=False`), `SESSION_COOKIE_SECURE = True` ensures transmission exclusively over HTTPS.
- **CSRF Cookies:** Hardened with `CSRF_COOKIE_SAMESITE = 'Lax'` and `CSRF_COOKIE_SECURE = True` in production environments.

### 3. Modern HTTP Defense Headers
Configured via `core.middleware.SecurityHeadersMiddleware` and Django core settings:
- **Content-Security-Policy (CSP):** Restricts script, style, font, connect, and media sources (`default-src 'self'`). Scripts are confined, Google Fonts allowed from designated origins (`fonts.googleapis.com`, `fonts.gstatic.com`), and frame framing prevented via `frame-ancestors 'none'`.
- **Referrer-Policy:** Strictly enforced as `strict-origin-when-cross-origin`, preserving user privacy while providing necessary origin information across same-origin requests.
- **Permissions-Policy:** Locks down browser capabilities: `camera=(), microphone=(), geolocation=(), payment=(), usb=()`.
- **Clickjacking Protection:** Defended in depth using `X_FRAME_OPTIONS = 'DENY'` combined with CSP `frame-ancestors 'none'`.
- **MIME Sniffing Prevention:** `SECURE_CONTENT_TYPE_NOSNIFF = True` (`X-Content-Type-Options: nosniff`).
- **Legacy XSS Filter:** `SECURE_BROWSER_XSS_FILTER = True` (`X-XSS-Protection: 1; mode=block`).

### 4. File Upload Hardening & Avatar Sanitization
Avatar uploads in `apps/accounts/forms.py` (`UserProfileForm.clean_profile_picture`) enforce strict boundaries:
- **File Size Ceiling:** Rejects files exceeding 5MB (`5 * 1024 * 1024` bytes).
- **Extension Whitelist:** Restricts allowed extensions strictly to `.jpg`, `.jpeg`, `.png`, and `.webp`.
- **PIL Header Verification:** Uses Pillow (`Image.open()` and `img.verify()`) to inspect binary headers and verify file integrity, immediately terminating and rejecting disguised payloads, polyglots, SVG XSS files, scripts, or executables.
- **Safe Stream Rewind:** Resets the file pointer (`seek(0)`) to maintain clean storage persistence.

### 5. Open-Redirect Prevention
All redirect handlers in `CustomLoginView` and `RegisterView` validate external URL parameters using Django's `url_has_allowed_host_and_scheme(url=next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure())`. Any target pointing to an external domain or untrusted protocol is safely discarded and defaulted to internal home/dashboard views.

### 6. Authentication & Password Security
- **Dual-Identifier Authentication:** Support for username or email via `EmailOrUsernameModelBackend` with case-insensitive lookup.
- **Password Policies:** Password strength enforced via standard Django validators (`UserAttributeSimilarityValidator`, `MinimumLengthValidator`, `CommonPasswordValidator`, `NumericPasswordValidator`).
- **Cryptographic Hashing:** Passwords hashed with PBKDF2 with SHA-256 (or Argon2 where configured), resistant to dictionary and GPU-based brute-force attacks.

### 7. Database Safety & ORM Parameterization
All database interactions use Django's ORM, inherently preventing SQL injection through parameterized queries and prepared statements.

---

## 🧪 Security Verification & Testing

Verify system security status anytime using automated checks:

```bash
# 1. Run deployment readiness security audit
uv run python manage.py check --deploy

# 2. Run automated security test suite
uv run python manage.py test apps.accounts.tests_security

# 3. Code formatting and linting
uv run ruff check .
```
