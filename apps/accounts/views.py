from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import TemplateView

from .forms import CustomLoginForm


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
        return render(request, self.template_name, {
            "form": form,
            "next": next_url,
            "page_title": "Sign In | Modern E-Commerce",
        })

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
            messages.success(request, f"Welcome back, {display_name}! You are successfully signed in.")

            return self._redirect_to_next_or_home(request, next_url)

        messages.error(
            request,
            "Authentication failed. Please verify your credentials and try again."
        )
        return render(request, self.template_name, {
            "form": form,
            "next": next_url,
            "page_title": "Sign In | Modern E-Commerce",
        })

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
            messages.info(request, f"Goodbye, {display_name}. You have been signed out.")
        else:
            messages.info(request, "You have been signed out.")
        return redirect(settings.LOGOUT_REDIRECT_URL)


class HomeView(TemplateView):
    """
    Landing and dashboard page showcasing the cohesive design system,
    theme switcher, logged-in status, and platform controls.
    """
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Home & Dashboard | Modern E-Commerce"
        return context
