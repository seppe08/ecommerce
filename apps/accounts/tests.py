from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

UserModel = get_user_model()


class AuthenticationAndLoginTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse("login")
        self.logout_url = reverse("logout")
        self.home_url = reverse("home")

        # Create active test user
        self.active_user = UserModel.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="SecurePassword123!",
            first_name="Jane",
            last_name="Doe",
        )

        # Create inactive test user
        self.inactive_user = UserModel.objects.create_user(
            username="inactiveuser",
            email="inactive@example.com",
            password="SecurePassword123!",
            is_active=False,
        )

    def test_login_page_renders_cleanly(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sign In")
        self.assertContains(response, "Username or Email")
        self.assertContains(response, "password-toggle-btn")
        self.assertContains(response, "theme-toggle-btn")

    def test_login_with_username_success(self):
        response = self.client.post(self.login_url, {
            "username_or_email": "testuser",
            "password": "SecurePassword123!",
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["user"].is_authenticated)
        self.assertEqual(response.context["user"].username, "testuser")
        self.assertContains(response, "Welcome back, Jane!")

    def test_login_with_email_success(self):
        response = self.client.post(self.login_url, {
            "username_or_email": "testuser@example.com",
            "password": "SecurePassword123!",
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["user"].is_authenticated)
        self.assertEqual(response.context["user"].email, "testuser@example.com")

    def test_login_case_insensitivity(self):
        # Email with uppercase characters
        response = self.client.post(self.login_url, {
            "username_or_email": "TestUser@EXAMPLE.com",
            "password": "SecurePassword123!",
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["user"].is_authenticated)

        # Username with uppercase characters
        self.client.logout()
        response = self.client.post(self.login_url, {
            "username_or_email": "TestUser",
            "password": "SecurePassword123!",
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["user"].is_authenticated)

    def test_login_with_invalid_password(self):
        response = self.client.post(self.login_url, {
            "username_or_email": "testuser",
            "password": "WrongPassword!",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["user"].is_authenticated)
        self.assertContains(response, "Invalid credentials")

    def test_login_with_nonexistent_user(self):
        response = self.client.post(self.login_url, {
            "username_or_email": "nonexistent@example.com",
            "password": "AnyPassword123!",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["user"].is_authenticated)
        self.assertContains(response, "No account was found")

    def test_login_with_inactive_user(self):
        response = self.client.post(self.login_url, {
            "username_or_email": "inactiveuser",
            "password": "SecurePassword123!",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["user"].is_authenticated)
        self.assertContains(response, "deactivated")

    def test_login_missing_fields_validation(self):
        response = self.client.post(self.login_url, {
            "username_or_email": "",
            "password": "",
        })
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIn("username_or_email", form.errors)
        self.assertIn("password", form.errors)

    def test_remember_me_session_expiry(self):
        # Remember me checked -> 30 days expiry
        response = self.client.post(self.login_url, {
            "username_or_email": "testuser",
            "password": "SecurePassword123!",
            "remember_me": "on",
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.get_expire_at_browser_close())
        self.assertEqual(self.client.session.get_expiry_age(), 60 * 60 * 24 * 30)

        # Remember me unchecked -> browser session (expires at browser close)
        self.client.logout()
        response = self.client.post(self.login_url, {
            "username_or_email": "testuser",
            "password": "SecurePassword123!",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get_expire_at_browser_close())

    def test_open_redirect_protection(self):
        # Malicious next URL should be rejected and redirected safely to home
        response = self.client.post(self.login_url, {
            "username_or_email": "testuser",
            "password": "SecurePassword123!",
            "next": "https://malicious-phishing-site.com",
        })
        self.assertRedirects(response, self.home_url)

    def test_authenticated_user_redirected_from_login(self):
        self.client.force_login(self.active_user)
        response = self.client.get(self.login_url)
        self.assertRedirects(response, self.home_url)

    def test_logout_flow(self):
        self.client.force_login(self.active_user)
        response = self.client.get(self.logout_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["user"].is_authenticated)
        self.assertContains(response, "signed out")
