from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import TemplateView

from apps.catalog.models import Category, Product

from .forms import (
    CustomLoginForm,
    CustomPasswordResetForm,
    CustomRegistrationForm,
    CustomSetPasswordForm,
    UserProfileForm,
)


class CustomLoginView(View):
    """
    Renders and processes the custom login flow with thorough validation,
    open-redirect protection, remember-me session persistence, and feedback.
    """

    template_name = "accounts/login.html"

    def get(self, request, *args, **kwargs):
        # Redirect authenticated users away from login
        if request.user.is_authenticated:
            return self._redirect_to_next_or_home(request)

        form = CustomLoginForm(request=request)
        next_url = request.GET.get("next", "")
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "next": next_url,
                "page_title": "Sign In | Modern E-Commerce",
            },
        )

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return self._redirect_to_next_or_home(request)

        form = CustomLoginForm(request=request, data=request.POST)
        next_url = request.POST.get("next") or request.GET.get("next", "")

        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)

            # Handle session expiry based on "Remember Me"
            if form.cleaned_data.get("remember_me"):
                # 30 days session
                request.session.set_expiry(60 * 60 * 24 * 30)
            else:
                # Browser session (expires when browser is closed)
                request.session.set_expiry(0)

            display_name = user.first_name if user.first_name else user.username
            messages.success(
                request,
                f"Welcome back, {display_name}! You are successfully signed in.",
            )

            return self._redirect_to_next_or_home(request, next_url)

        messages.error(
            request,
            "Authentication failed. Please verify your credentials and try again.",
        )
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "next": next_url,
                "page_title": "Sign In | Modern E-Commerce",
            },
        )

    def _redirect_to_next_or_home(self, request, next_url=""):
        if next_url and url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(next_url)
        return redirect(settings.LOGIN_REDIRECT_URL)


class CustomLogoutView(View):
    """
    Safely logs out the current user and redirects to login with confirmation.
    Supports both POST and GET for UX convenience.
    """

    def get(self, request, *args, **kwargs):
        return self._do_logout(request)

    def post(self, request, *args, **kwargs):
        return self._do_logout(request)

    def _do_logout(self, request):
        if request.user.is_authenticated:
            display_name = request.user.first_name or request.user.username
            auth_logout(request)
            messages.info(
                request, f"Goodbye, {display_name}. You have been signed out."
            )
        else:
            messages.info(request, "You have been signed out.")
        return redirect(settings.LOGOUT_REDIRECT_URL)


class RegisterView(View):
    """
    Renders and processes user registration with password confirmation,
    password policy validation, automatic login upon sign-up, and
    WCAG AA accessible error messaging.
    """

    template_name = "accounts/register.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)

        form = CustomRegistrationForm()
        next_url = request.GET.get("next", "")
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "next": next_url,
                "page_title": "Create Account — AuraStore",
            },
        )

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)

        form = CustomRegistrationForm(data=request.POST)
        next_url = request.POST.get("next") or request.GET.get("next", "")

        if form.is_valid():
            user = form.save()
            auth_login(
                request,
                user,
                backend="apps.accounts.backends.EmailOrUsernameModelBackend",
            )

            display_name = user.first_name if user.first_name else user.username
            messages.success(
                request,
                f"Welcome to AuraStore, {display_name}! Your account has been created successfully.",
            )
            if next_url and url_has_allowed_host_and_scheme(
                url=next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)
            return redirect(settings.LOGIN_REDIRECT_URL)

        messages.error(
            request,
            "Registration failed. Please check the information you entered below.",
        )
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "next": next_url,
                "page_title": "Create Account — AuraStore",
            },
        )


class ProfileView(LoginRequiredMixin, View):
    """
    User profile management view allowing authenticated users to update
    their personal details, phone number, date of birth, and avatar.
    """

    template_name = "accounts/profile.html"
    login_url = "login"

    def get(self, request, *args, **kwargs):
        form = UserProfileForm(instance=request.user)
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "page_title": "My Profile — AuraStore",
            },
        )

    def post(self, request, *args, **kwargs):
        form = UserProfileForm(
            request.POST,
            request.FILES,
            instance=request.user,
        )
        if form.is_valid():
            form.save()
            messages.success(
                request, "Your profile information has been saved successfully."
            )
            return redirect("profile")

        messages.error(
            request,
            "Unable to update profile. Please correct the errors highlighted below.",
        )
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "page_title": "My Profile — AuraStore",
            },
        )


class CustomPasswordResetView(auth_views.PasswordResetView):
    """
    Renders and handles the request to send a password reset email.
    """

    template_name = "accounts/password_reset_form.html"
    form_class = CustomPasswordResetForm
    email_template_name = "accounts/password_reset_email.html"
    subject_template_name = "accounts/password_reset_subject.txt"
    success_url = reverse_lazy("password_reset_done")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Reset Your Password — AuraStore"
        return context


class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    """
    Informs user that password reset instructions have been dispatched.
    """

    template_name = "accounts/password_reset_done.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Check Your Inbox — AuraStore"
        return context


class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    """
    Allows user to specify a new password using token validation.
    """

    template_name = "accounts/password_reset_confirm.html"
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy("password_reset_complete")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Set New Password — AuraStore"
        return context


class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    """
    Informs user that their password was successfully reset.
    """

    template_name = "accounts/password_reset_complete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Password Reset Successful — AuraStore"
        return context


class HomeView(TemplateView):
    """
    Landing and dashboard page showcasing the editorial retail storefront,
    featured collections, category navigation, and logged-in member status.
    """

    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "AuraStore — Modern Living & Editorial Storefront"
        featured = (
            Product.objects.filter(is_active=True, featured=True)
            .select_related("category")
            .prefetch_related("images")[:8]
        )
        if not featured.exists():
            featured = (
                Product.objects.filter(is_active=True)
                .select_related("category")
                .prefetch_related("images")[:8]
            )
        context["featured_products"] = featured
        context["categories"] = Category.objects.filter(is_active=True).annotate(
            product_count=Count("products", filter=Q(products__is_active=True))
        )
        return context
