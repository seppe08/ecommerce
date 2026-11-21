import io

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from apps.accounts.forms import UserProfileForm

UserModel = get_user_model()


def create_in_memory_image(file_format="JPEG", size=(50, 50), color="blue"):
    """Helper to generate in-memory image bytes using Pillow."""
    image = Image.new("RGB", size, color=color)
    output = io.BytesIO()
    image.save(output, format=file_format)
    output.seek(0)
    return output.getvalue()


class SecurityHeadersTestCase(TestCase):
    """
    Validates that modern security headers (CSP, Referrer-Policy, Permissions-Policy,
    X-Frame-Options, X-Content-Type-Options) are injected into HTTP responses.
    """

    def test_security_headers_present_on_home(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

        # Content-Security-Policy
        self.assertIn("Content-Security-Policy", response.headers)
        csp = response.headers["Content-Security-Policy"]
        self.assertIn("default-src 'self'", csp)
        self.assertIn("frame-ancestors 'none'", csp)
        self.assertIn("fonts.googleapis.com", csp)

        # Referrer-Policy
        self.assertIn("Referrer-Policy", response.headers)
        self.assertEqual(
            response.headers["Referrer-Policy"],
            "strict-origin-when-cross-origin",
        )

        # Permissions-Policy
        self.assertIn("Permissions-Policy", response.headers)
        permissions = response.headers["Permissions-Policy"]
        self.assertIn("camera=()", permissions)
        self.assertIn("microphone=()", permissions)
        self.assertIn("geolocation=()", permissions)

        # X-Frame-Options
        self.assertIn("X-Frame-Options", response.headers)
        self.assertEqual(response.headers["X-Frame-Options"], "DENY")

        # X-Content-Type-Options
        self.assertIn("X-Content-Type-Options", response.headers)
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")

    def test_security_headers_present_on_login(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("Content-Security-Policy", response.headers)
        self.assertIn("Referrer-Policy", response.headers)
        self.assertIn("Permissions-Policy", response.headers)


class SecuritySettingsTestCase(TestCase):
    """
    Validates that core security settings and flags adhere to production standards.
    """

    def test_session_cookie_settings(self):
        self.assertTrue(settings.SESSION_COOKIE_HTTPONLY)
        self.assertEqual(settings.SESSION_COOKIE_SAMESITE, "Lax")

    def test_csrf_cookie_settings(self):
        self.assertFalse(settings.CSRF_COOKIE_HTTPONLY)
        self.assertEqual(settings.CSRF_COOKIE_SAMESITE, "Lax")

    def test_browser_defenses_settings(self):
        self.assertTrue(settings.SECURE_BROWSER_XSS_FILTER)
        self.assertTrue(settings.SECURE_CONTENT_TYPE_NOSNIFF)
        self.assertEqual(settings.X_FRAME_OPTIONS, "DENY")

    def test_hsts_settings_configured(self):
        self.assertTrue(hasattr(settings, "SECURE_HSTS_SECONDS"))
        self.assertTrue(settings.SECURE_HSTS_INCLUDE_SUBDOMAINS)
        self.assertTrue(settings.SECURE_HSTS_PRELOAD)

    @override_settings(
        DEBUG=False,
        SESSION_COOKIE_SECURE=True,
        CSRF_COOKIE_SECURE=True,
    )
    def test_secure_cookies_in_simulated_production(self):
        self.assertTrue(settings.SESSION_COOKIE_SECURE)
        self.assertTrue(settings.CSRF_COOKIE_SECURE)


class FileUploadSecurityTestCase(TestCase):
    """
    Validates file upload boundaries, format whitelisting, byte-level PIL header
    verification, and defense against SVG XSS, script payloads, and fake images.
    """

    def setUp(self):
        self.user = UserModel.objects.create_user(
            username="uploadtester",
            email="upload@example.com",
            password="StrongPassword123!",
        )

    def test_valid_jpeg_upload_accepted(self):
        image_bytes = create_in_memory_image(file_format="JPEG")
        uploaded = SimpleUploadedFile(
            "avatar.jpg", image_bytes, content_type="image/jpeg"
        )
        form = UserProfileForm(
            data={"first_name": "Test", "last_name": "User"},
            files={"profile_picture": uploaded},
            instance=self.user,
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_valid_png_upload_accepted(self):
        image_bytes = create_in_memory_image(file_format="PNG")
        uploaded = SimpleUploadedFile(
            "avatar.png", image_bytes, content_type="image/png"
        )
        form = UserProfileForm(
            data={"first_name": "Test", "last_name": "User"},
            files={"profile_picture": uploaded},
            instance=self.user,
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_valid_webp_upload_accepted(self):
        image_bytes = create_in_memory_image(file_format="WEBP")
        uploaded = SimpleUploadedFile(
            "avatar.webp", image_bytes, content_type="image/webp"
        )
        form = UserProfileForm(
            data={"first_name": "Test", "last_name": "User"},
            files={"profile_picture": uploaded},
            instance=self.user,
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_oversized_file_rejected(self):
        # Generate valid JPEG header with appended data exceeding 5MB
        valid_jpeg = create_in_memory_image(file_format="JPEG")
        oversized_data = valid_jpeg + (b"0" * (5 * 1024 * 1024 + 1024))
        uploaded = SimpleUploadedFile(
            "large.jpg", oversized_data, content_type="image/jpeg"
        )
        form = UserProfileForm(
            data={"first_name": "Test"},
            files={"profile_picture": uploaded},
            instance=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("profile_picture", form.errors)
        self.assertTrue(
            any("5MB" in err for err in form.errors["profile_picture"]),
        )

    def test_disallowed_extension_rejected(self):
        image_bytes = create_in_memory_image(file_format="JPEG")
        dangerous_names = [
            "exploit.svg",
            "payload.php",
            "script.sh",
            "run.exe",
            "file.js",
        ]
        for filename in dangerous_names:
            uploaded = SimpleUploadedFile(
                filename, image_bytes, content_type="application/octet-stream"
            )
            form = UserProfileForm(
                data={"first_name": "Test"},
                files={"profile_picture": uploaded},
                instance=self.user,
            )
            self.assertFalse(form.is_valid(), f"Expected {filename} to be rejected")
            self.assertIn("profile_picture", form.errors)

    def test_svg_xss_disguised_as_png_rejected(self):
        svg_xss_payload = (
            b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>'
        )
        uploaded = SimpleUploadedFile(
            "avatar.png", svg_xss_payload, content_type="image/png"
        )
        form = UserProfileForm(
            data={"first_name": "Test"},
            files={"profile_picture": uploaded},
            instance=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("profile_picture", form.errors)

    def test_script_disguised_as_jpeg_rejected(self):
        script_payload = b'#!/usr/bin/env python\nimport os\nos.system("id")'
        uploaded = SimpleUploadedFile(
            "avatar.jpg", script_payload, content_type="image/jpeg"
        )
        form = UserProfileForm(
            data={"first_name": "Test"},
            files={"profile_picture": uploaded},
            instance=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("profile_picture", form.errors)

    def test_corrupted_image_rejected(self):
        corrupt_bytes = b"\xff\xd8\xff\xe0" + b"\x00" * 20  # Incomplete JPEG header
        uploaded = SimpleUploadedFile(
            "broken.jpg", corrupt_bytes, content_type="image/jpeg"
        )
        form = UserProfileForm(
            data={"first_name": "Test"},
            files={"profile_picture": uploaded},
            instance=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("profile_picture", form.errors)

    def test_bmp_format_disguised_as_png_rejected(self):
        bmp_bytes = create_in_memory_image(file_format="BMP")
        uploaded = SimpleUploadedFile(
            "disguised.png", bmp_bytes, content_type="image/png"
        )
        form = UserProfileForm(
            data={"first_name": "Test"},
            files={"profile_picture": uploaded},
            instance=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("profile_picture", form.errors)

    def test_update_profile_without_file_change_succeeds(self):
        form = UserProfileForm(
            data={"first_name": "UpdatedName", "last_name": "UpdatedLast"},
            instance=self.user,
        )
        self.assertTrue(form.is_valid(), form.errors)


class OpenRedirectSecurityTestCase(TestCase):
    """
    Validates open-redirect defense in login and registration flows.
    """

    def setUp(self):
        self.user = UserModel.objects.create_user(
            username="redirectuser",
            email="redirect@example.com",
            password="ValidPassword123!",
        )

    def test_login_safe_internal_redirect(self):
        login_url = reverse("login")
        safe_next = reverse("catalog:product_list")
        response = self.client.post(
            login_url,
            {
                "username_or_email": "redirectuser",
                "password": "ValidPassword123!",
                "next": safe_next,
            },
        )
        self.assertRedirects(response, safe_next)

    def test_login_evil_external_redirect_blocked(self):
        login_url = reverse("login")
        response = self.client.post(
            login_url,
            {
                "username_or_email": "redirectuser",
                "password": "ValidPassword123!",
                "next": "https://evil-phishing-site.com/steal",
            },
        )
        # Must redirect safely to internal default home, NOT evil external url
        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL))

    def test_login_protocol_relative_redirect_blocked(self):
        login_url = reverse("login")
        response = self.client.post(
            login_url,
            {
                "username_or_email": "redirectuser",
                "password": "ValidPassword123!",
                "next": "//evil-phishing-site.com/steal",
            },
        )
        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL))

    def test_login_javascript_scheme_blocked(self):
        login_url = reverse("login")
        response = self.client.post(
            login_url,
            {
                "username_or_email": "redirectuser",
                "password": "ValidPassword123!",
                "next": "javascript:alert(document.cookie)",
            },
        )
        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL))

    def test_register_safe_internal_redirect(self):
        register_url = reverse("register")
        safe_next = reverse("profile")
        response = self.client.post(
            register_url,
            {
                "username": "newsecureuser",
                "email": "newsecure@example.com",
                "password": "StrongPassword987!",
                "password_confirm": "StrongPassword987!",
                "next": safe_next,
            },
        )
        self.assertRedirects(response, safe_next)

    def test_register_evil_external_redirect_blocked(self):
        register_url = reverse("register")
        response = self.client.post(
            register_url,
            {
                "username": "anothernewuser",
                "email": "anothernew@example.com",
                "password": "StrongPassword987!",
                "password_confirm": "StrongPassword987!",
                "next": "https://attacker.org/exfiltrate",
            },
        )
        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL))
