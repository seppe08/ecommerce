import re
from datetime import date

from django import forms

from .models import Order


class OrderCreateForm(forms.ModelForm):
    """
    Checkout form capturing customer information and shipping details
    with accessible styling and autocomplete hints.
    """

    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "Jane",
                "autocomplete": "given-name",
                "required": "required",
            }
        ),
    )
    last_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "Doe",
                "autocomplete": "family-name",
                "required": "required",
            }
        ),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "form-input",
                "placeholder": "jane.doe@example.com",
                "autocomplete": "email",
                "required": "required",
            }
        ),
    )
    phone = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "+1 (555) 000-0000",
                "autocomplete": "tel",
            }
        ),
    )
    address = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "123 Market Street, Apt 4B",
                "autocomplete": "street-address",
                "required": "required",
            }
        ),
    )
    city = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "San Francisco",
                "autocomplete": "address-level2",
                "required": "required",
            }
        ),
    )
    postal_code = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "94105",
                "autocomplete": "postal-code",
                "required": "required",
            }
        ),
    )
    country = forms.CharField(
        max_length=100,
        required=True,
        initial="United States",
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "United States",
                "autocomplete": "country-name",
                "required": "required",
            }
        ),
    )
    payment_method = forms.ChoiceField(
        choices=(
            ("stripe", "Credit or Debit Card (Stripe)"),
            ("cod", "Cash on Delivery"),
        ),
        initial="stripe",
        widget=forms.RadioSelect(attrs={"class": "payment-method-radio"}),
        required=False,
    )
    save_address = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={"class": "form-checkbox"}),
        label="Save this address for future purchases",
    )

    class Meta:
        model = Order
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone",
            "address",
            "city",
            "postal_code",
            "country",
            "payment_method",
        )

    def clean_payment_method(self):
        return self.cleaned_data.get("payment_method") or "stripe"


class CardPaymentForm(forms.Form):
    """
    Card payment form with client and server validation for Stripe / Card processing.
    """

    cardholder_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "Jane Doe",
                "autocomplete": "cc-name",
                "required": "required",
            }
        ),
    )
    card_number = forms.CharField(
        max_length=23,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "4242 4242 4242 4242",
                "autocomplete": "cc-number",
                "inputmode": "numeric",
                "pattern": "[0-9 ]+",
                "required": "required",
            }
        ),
    )
    expiry = forms.CharField(
        max_length=7,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "MM / YY",
                "autocomplete": "cc-exp",
                "required": "required",
            }
        ),
    )
    cvc = forms.CharField(
        max_length=4,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "123",
                "autocomplete": "cc-csc",
                "inputmode": "numeric",
                "required": "required",
            }
        ),
    )

    def clean_card_number(self):
        number = self.cleaned_data["card_number"].replace(" ", "").replace("-", "")
        if not number.isdigit() or len(number) < 13 or len(number) > 19:
            raise forms.ValidationError(
                "Please enter a valid card number (13-19 digits)."
            )
        return number

    def clean_expiry(self):
        expiry = self.cleaned_data["expiry"].strip()
        match = re.fullmatch(r"(0[1-9]|1[0-2])\s*/\s*(\d{2}|\d{4})", expiry)
        if not match:
            raise forms.ValidationError("Enter a valid expiry date in MM/YY format.")
        month = int(match.group(1))
        year_raw = match.group(2)
        year = int(year_raw) if len(year_raw) == 4 else 2000 + int(year_raw)
        today = date.today()
        if (year, month) < (today.year, today.month):
            raise forms.ValidationError("This card has expired.")
        return f"{month:02d}/{year % 100:02d}"

    def clean_cvc(self):
        cvc = self.cleaned_data["cvc"].strip()
        if not cvc.isdigit() or len(cvc) not in (3, 4):
            raise forms.ValidationError("CVC must be 3 or 4 digits.")
        return cvc
