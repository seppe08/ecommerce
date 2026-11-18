from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Q

UserModel = get_user_model()


class CustomLoginForm(forms.Form):
    """
    Robust, production-grade custom login form supporting both username
    and email identification, strict validation, helpful error messaging,
    and 'remember me' session persistence.
    """
    username_or_email = forms.CharField(
        label="Username or Email",
        max_length=254,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "name@example.com or username",
                "autocomplete": "username",
                "autocapitalize": "none",
                "autocorrect": "off",
                "spellcheck": "false",
                "id": "id_username_or_email",
            }
        ),
        error_messages={
            "required": "Please enter your username or email address.",
        },
    )

    password = forms.CharField(
        label="Password",
        strip=False,
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your password",
                "autocomplete": "current-password",
                "id": "id_password",
            }
        ),
        error_messages={
            "required": "Please enter your account password.",
        },
    )

    remember_me = forms.BooleanField(
        label="Remember me for 30 days",
        required=False,
        initial=False,
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-checkbox",
                "id": "id_remember_me",
            }
        ),
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean_username_or_email(self):
        username_or_email = self.cleaned_data.get("username_or_email", "").strip()
        if not username_or_email:
            raise ValidationError(
                "Please provide a valid username or email address.",
                code="required",
            )
        return username_or_email

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if not password:
            raise ValidationError(
                "Please enter your password.",
                code="required",
            )
        return password

    def clean(self):
        cleaned_data = super().clean()
        identifier = cleaned_data.get("username_or_email")
        password = cleaned_data.get("password")

        if identifier and password:
            # Authenticate via custom backend
            self.user_cache = authenticate(
                self.request,
                username=identifier,
                password=password,
            )

            if self.user_cache is None:
                # Provide granular, helpful feedback
                user_match = UserModel.objects.filter(
                    Q(username__iexact=identifier) | Q(email__iexact=identifier)
                ).first()

                if user_match:
                    if not user_match.is_active:
                        raise ValidationError(
                            "This account is currently deactivated. Please contact support for assistance.",
                            code="inactive",
                        )
                    else:
                        raise ValidationError(
                            "Invalid credentials. The password you entered is incorrect. Please check your password and try again.",
                            code="invalid_credentials",
                        )
                else:
                    raise ValidationError(
                        "No account was found with that username or email address. Please double-check your spelling or sign up.",
                        code="user_not_found",
                    )
            else:
                self.confirm_login_allowed(self.user_cache)

        return cleaned_data

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise ValidationError(
                "This account is inactive. Please contact support.",
                code="inactive",
            )

    def get_user(self):
        return self.user_cache
