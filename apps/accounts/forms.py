from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.password_validation import validate_password
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
        help_text="Use the username or email address linked to your account.",
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
        help_text="Passwords are case-sensitive.",
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


class CustomRegistrationForm(forms.ModelForm):
    """
    Form for new user registration with unique email validation,
    strict password complexity checks via Django's password validators,
    and password confirmation matching.
    """
    username = forms.CharField(
        label="Username",
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Choose a username (e.g. alex99)",
                "autocomplete": "username",
                "autocapitalize": "none",
                "autocorrect": "off",
                "spellcheck": "false",
                "id": "id_username",
            }
        ),
        help_text="Letters, digits, and @/./+/-/_ only. Up to 150 characters.",
        error_messages={
            "required": "Please choose a username for your account.",
        },
    )

    email = forms.EmailField(
        label="Email address",
        max_length=254,
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "name@example.com",
                "autocomplete": "email",
                "autocapitalize": "none",
                "autocorrect": "off",
                "spellcheck": "false",
                "id": "id_email",
            }
        ),
        help_text="We will never share your email address. Used for order updates and sign in.",
        error_messages={
            "required": "Please enter your email address.",
            "invalid": "Please enter a valid email address.",
        },
    )

    password = forms.CharField(
        label="Password",
        strip=False,
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control has-trailing-btn",
                "placeholder": "Create a strong password",
                "autocomplete": "new-password",
                "id": "id_password",
            }
        ),
        help_text="Must contain at least 8 characters and cannot be entirely numeric.",
        error_messages={
            "required": "Please enter a password.",
        },
    )

    password_confirm = forms.CharField(
        label="Confirm password",
        strip=False,
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control has-trailing-btn",
                "placeholder": "Re-enter your password",
                "autocomplete": "new-password",
                "id": "id_password_confirm",
            }
        ),
        help_text="Re-enter your password exactly as typed above.",
        error_messages={
            "required": "Please confirm your password.",
        },
    )

    class Meta:
        model = UserModel
        fields = ("username", "email")

    def clean_username(self):
        username = self.cleaned_data.get("username", "").strip()
        if UserModel.objects.filter(username__iexact=username).exists():
            raise ValidationError(
                "A user with that username already exists. Please choose a different one.",
                code="username_taken",
            )
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if UserModel.objects.filter(email__iexact=email).exists():
            raise ValidationError(
                "An account with this email address already exists. Please sign in or use another email.",
                code="email_taken",
            )
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm:
            if password != password_confirm:
                self.add_error(
                    "password_confirm",
                    ValidationError(
                        "The two password fields did not match. Please re-enter your password.",
                        code="password_mismatch",
                    ),
                )
            else:
                temp_user = UserModel(
                    username=cleaned_data.get("username", ""),
                    email=cleaned_data.get("email", ""),
                )
                try:
                    validate_password(password, user=temp_user)
                except ValidationError as error:
                    self.add_error("password", error)

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """
    Profile management form allowing users to update their personal information,
    phone number, birth date, and avatar profile picture.
    """
    first_name = forms.CharField(
        label="First Name",
        max_length=150,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "e.g. Jane",
                "autocomplete": "given-name",
                "id": "id_first_name",
            }
        ),
    )

    last_name = forms.CharField(
        label="Last Name",
        max_length=150,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "e.g. Doe",
                "autocomplete": "family-name",
                "id": "id_last_name",
            }
        ),
    )

    phone = forms.CharField(
        label="Phone Number",
        max_length=15,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "e.g. +1-555-234-5678",
                "autocomplete": "tel",
                "id": "id_phone",
            }
        ),
        help_text="Optional. Max 15 chars (e.g. +1-555-234-5678). Used for delivery and security alerts.",
    )

    birth_date = forms.DateField(
        label="Date of Birth",
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
                "id": "id_birth_date",
            }
        ),
        help_text="Optional. Used to send special birthday gifts and offers.",
    )

    profile_picture = forms.ImageField(
        label="Profile Picture / Avatar",
        required=False,
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-control-file",
                "id": "id_profile_picture",
                "accept": "image/*",
            }
        ),
        help_text="Upload a JPEG, PNG, or WebP image.",
    )

    class Meta:
        model = UserModel
        fields = ("first_name", "last_name", "phone", "birth_date", "profile_picture")

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "")
        if phone:
            phone = phone.strip()
            allowed_chars = set("+0123456789 -().")
            if not all(c in allowed_chars for c in phone):
                raise ValidationError(
                    "Please enter a valid phone number containing digits and standard punctuation.",
                    code="invalid_phone",
                )
        return phone


class CustomPasswordResetForm(PasswordResetForm):
    """
    Accessible, styled password reset form supporting case-insensitive
    email lookup and clear feedback.
    """
    email = forms.EmailField(
        label="Email Address",
        max_length=254,
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "name@example.com",
                "autocomplete": "email",
                "autocapitalize": "none",
                "autocorrect": "off",
                "spellcheck": "false",
                "id": "id_email",
            }
        ),
        help_text="Enter the email address associated with your AuraStore account.",
        error_messages={
            "required": "Please provide your email address.",
            "invalid": "Please enter a valid email address.",
        },
    )

    def get_users(self, email):
        """Given an email, return matching active user(s) case-insensitively."""
        email = (email or "").strip()
        active_users = UserModel._default_manager.filter(
            email__iexact=email,
            is_active=True,
        )
        return (
            u
            for u in active_users
            if u.has_usable_password()
        )


class CustomSetPasswordForm(SetPasswordForm):
    """
    Styled new-password form for the password reset confirmation step,
    incorporating password visibility toggles and WCAG compliance.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_password1"].widget = forms.PasswordInput(
            attrs={
                "class": "form-control has-trailing-btn",
                "placeholder": "Enter your new password",
                "autocomplete": "new-password",
                "id": "id_new_password1",
            }
        )
        self.fields["new_password1"].help_text = (
            "Must contain at least 8 characters and cannot be entirely numeric."
        )

        self.fields["new_password2"].widget = forms.PasswordInput(
            attrs={
                "class": "form-control has-trailing-btn",
                "placeholder": "Confirm your new password",
                "autocomplete": "new-password",
                "id": "id_new_password2",
            }
        )
        self.fields["new_password2"].help_text = "Re-enter your new password to verify."
