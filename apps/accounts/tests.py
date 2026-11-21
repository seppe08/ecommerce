from io import BytesIO

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from PIL import Image

UserModel = get_user_model()


def get_dummy_avatar():
    file = BytesIO()
    image = Image.new("RGB", (64, 64), color="indigo")
    image.save(file, "JPEG")
    file.seek(0)
    return SimpleUploadedFile("test_avatar.jpg", file.read(), content_type="image/jpeg")


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
        response = self.client.post(
            self.login_url,
            {
                "username_or_email": "testuser",
                "password": "SecurePassword123!",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["user"].is_authenticated)
        self.assertEqual(response.context["user"].username, "testuser")
        self.assertContains(response, "Welcome back, Jane!")

    def test_login_with_email_success(self):
        response = self.client.post(
            self.login_url,
            {
                "username_or_email": "testuser@example.com",
                "password": "SecurePassword123!",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["user"].is_authenticated)
        self.assertEqual(response.context["user"].email, "testuser@example.com")

    def test_login_case_insensitivity(self):
        # Email with uppercase characters
        response = self.client.post(
            self.login_url,
            {
                "username_or_email": "TestUser@EXAMPLE.com",
                "password": "SecurePassword123!",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["user"].is_authenticated)

        # Username with uppercase characters
        self.client.logout()
        response = self.client.post(
            self.login_url,
            {
                "username_or_email": "TestUser",
                "password": "SecurePassword123!",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["user"].is_authenticated)

    def test_login_with_invalid_password(self):
        response = self.client.post(
            self.login_url,
            {
                "username_or_email": "testuser",
                "password": "WrongPassword!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["user"].is_authenticated)
        self.assertContains(response, "Invalid credentials")

    def test_login_with_nonexistent_user(self):
        response = self.client.post(
            self.login_url,
            {
                "username_or_email": "nonexistent@example.com",
                "password": "AnyPassword123!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["user"].is_authenticated)
        self.assertContains(response, "No account was found")

    def test_login_with_inactive_user(self):
        response = self.client.post(
            self.login_url,
            {
                "username_or_email": "inactiveuser",
                "password": "SecurePassword123!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["user"].is_authenticated)
        self.assertContains(response, "deactivated")

    def test_login_missing_fields_validation(self):
        response = self.client.post(
            self.login_url,
            {
                "username_or_email": "",
                "password": "",
            },
        )
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIn("username_or_email", form.errors)
        self.assertIn("password", form.errors)

    def test_remember_me_session_expiry(self):
        # Remember me checked -> 30 days expiry
        response = self.client.post(
            self.login_url,
            {
                "username_or_email": "testuser",
                "password": "SecurePassword123!",
                "remember_me": "on",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.get_expire_at_browser_close())
        self.assertEqual(self.client.session.get_expiry_age(), 60 * 60 * 24 * 30)

        # Remember me unchecked -> browser session (expires at browser close)
        self.client.logout()
        response = self.client.post(
            self.login_url,
            {
                "username_or_email": "testuser",
                "password": "SecurePassword123!",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get_expire_at_browser_close())

    def test_open_redirect_protection(self):
        # Malicious next URL should be rejected and redirected safely to home
        response = self.client.post(
            self.login_url,
            {
                "username_or_email": "testuser",
                "password": "SecurePassword123!",
                "next": "https://malicious-phishing-site.com",
            },
        )
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


class UserRegistrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse("register")
        self.home_url = reverse("home")
        self.existing_user = UserModel.objects.create_user(
            username="existinguser",
            email="existing@example.com",
            password="ExistingPassword123!",
        )

    def test_register_page_renders_cleanly(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create your account")
        self.assertContains(response, "Exclusive Member Perks")
        self.assertContains(response, "id_username")
        self.assertContains(response, "id_email")
        self.assertContains(response, "id_password")
        self.assertContains(response, "id_password_confirm")

    def test_authenticated_user_redirected_from_register(self):
        self.client.force_login(self.existing_user)
        response = self.client.get(self.register_url)
        self.assertRedirects(response, self.home_url)

    def test_successful_registration(self):
        response = self.client.post(
            self.register_url,
            {
                "username": "brandnewuser",
                "email": "brandnew@example.com",
                "password": "ComplexPassword123!",
                "password_confirm": "ComplexPassword123!",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["user"].is_authenticated)
        self.assertEqual(response.context["user"].username, "brandnewuser")
        self.assertContains(response, "Welcome to AuraStore, brandnewuser!")

        # Verify DB entry
        user = UserModel.objects.get(username="brandnewuser")
        self.assertEqual(user.email, "brandnew@example.com")
        self.assertTrue(user.check_password("ComplexPassword123!"))

    def test_registration_with_existing_email(self):
        response = self.client.post(
            self.register_url,
            {
                "username": "anotheruniqueuser",
                "email": "EXISTING@example.com",  # case-insensitive clash
                "password": "ComplexPassword123!",
                "password_confirm": "ComplexPassword123!",
            },
        )
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIn("email", form.errors)
        self.assertContains(response, "already exists")
        self.assertFalse(
            UserModel.objects.filter(username="anotheruniqueuser").exists()
        )

    def test_registration_with_existing_username(self):
        response = self.client.post(
            self.register_url,
            {
                "username": "ExistingUser",  # case-insensitive clash
                "email": "newuniqueemail@example.com",
                "password": "ComplexPassword123!",
                "password_confirm": "ComplexPassword123!",
            },
        )
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIn("username", form.errors)
        self.assertContains(response, "already exists")

    def test_registration_password_mismatch(self):
        response = self.client.post(
            self.register_url,
            {
                "username": "mismatchuser",
                "email": "mismatch@example.com",
                "password": "ComplexPassword123!",
                "password_confirm": "DifferentPassword123!",
            },
        )
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIn("password_confirm", form.errors)
        self.assertContains(response, "did not match")

    def test_registration_weak_password_rejected(self):
        # Test password too short or common
        response = self.client.post(
            self.register_url,
            {
                "username": "weakpwuser",
                "email": "weak@example.com",
                "password": "123",
                "password_confirm": "123",
            },
        )
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIn("password", form.errors)


class UserProfileManagementTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.profile_url = reverse("profile")
        self.login_url = reverse("login")
        self.user = UserModel.objects.create_user(
            username="profiletester",
            email="profiletester@example.com",
            password="SecurePassword123!",
            first_name="Arthur",
            last_name="Dent",
            phone="+1234567890",
            birth_date="1980-04-12",
        )

    def test_unauthenticated_profile_access_redirects_to_login(self):
        response = self.client.get(self.profile_url)
        expected_redirect = f"{self.login_url}?next={self.profile_url}"
        self.assertRedirects(response, expected_redirect)

    def test_authenticated_profile_renders_user_data(self):
        self.client.force_login(self.user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Arthur Dent")
        self.assertContains(response, "profiletester@example.com")
        self.assertContains(response, "+1234567890")
        self.assertContains(response, "Personal Information")

    def test_profile_update_successful(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.profile_url,
            {
                "first_name": "Ford",
                "last_name": "Prefect",
                "phone": "+1-555-999-8888",
                "birth_date": "1985-06-20",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "saved successfully")

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Ford")
        self.assertEqual(self.user.last_name, "Prefect")
        self.assertEqual(self.user.phone, "+1-555-999-8888")
        self.assertEqual(str(self.user.birth_date), "1985-06-20")

    def test_profile_invalid_phone_rejected(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.profile_url,
            {
                "first_name": "Ford",
                "last_name": "Prefect",
                "phone": "INVALID_PHONE_#$$$%",
            },
        )
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIn("phone", form.errors)

    def test_profile_picture_upload(self):
        self.client.force_login(self.user)
        avatar = get_dummy_avatar()
        response = self.client.post(
            self.profile_url,
            {
                "first_name": "Arthur",
                "last_name": "Dent",
                "phone": "+1234567890",
                "profile_picture": avatar,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(bool(self.user.profile_picture))
        self.assertIn("test_avatar", self.user.profile_picture.name)


class PasswordResetWorkflowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.reset_url = reverse("password_reset")
        self.reset_done_url = reverse("password_reset_done")
        self.reset_complete_url = reverse("password_reset_complete")
        self.user = UserModel.objects.create_user(
            username="resetuser",
            email="resetuser@example.com",
            password="OriginalPassword123!",
        )

    def test_password_reset_form_renders(self):
        response = self.client.get(self.reset_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reset your password")
        self.assertContains(response, "id_email")
        self.assertContains(response, "Send Password Reset Link")

    def test_password_reset_email_dispatched(self):
        mail.outbox = []
        response = self.client.post(
            self.reset_url,
            {
                "email": "resetuser@example.com",
            },
        )
        self.assertRedirects(response, self.reset_done_url)
        self.assertEqual(len(mail.outbox), 1)
        dispatched_email = mail.outbox[0]
        self.assertIn("Reset your AuraStore account password", dispatched_email.subject)
        self.assertIn("resetuser@example.com", dispatched_email.to)
        self.assertIn("/reset/", dispatched_email.body)

    def test_password_reset_done_renders(self):
        response = self.client.get(self.reset_done_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Check your email inbox")

    def test_password_reset_confirm_with_valid_token(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        confirm_url = reverse(
            "password_reset_confirm", kwargs={"uidb64": uid, "token": token}
        )

        # GET should follow session redirect and render new password form
        response = self.client.get(confirm_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["validlink"])
        self.assertContains(response, "Choose a new password")
        self.assertContains(response, "id_new_password1")
        self.assertContains(response, "id_new_password2")

        # POST valid new passwords to the active view path
        post_response = self.client.post(
            response.request["PATH_INFO"],
            {
                "new_password1": "NewlySetPassword999!",
                "new_password2": "NewlySetPassword999!",
            },
        )
        self.assertRedirects(post_response, self.reset_complete_url)

        # Confirm password actually changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewlySetPassword999!"))

    def test_password_reset_confirm_with_invalid_token(self):
        confirm_url = reverse(
            "password_reset_confirm",
            kwargs={"uidb64": "invalid-uid", "token": "invalid-token"},
        )
        response = self.client.get(confirm_url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["validlink"])
        self.assertContains(response, "Reset Link Expired or Invalid")

    def test_password_reset_complete_renders(self):
        response = self.client.get(self.reset_complete_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Password updated successfully")
        self.assertContains(response, reverse("login"))
