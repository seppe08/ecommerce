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
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Jane',
            'autocomplete': 'given-name',
            'required': 'required',
        }),
    )
    last_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Doe',
            'autocomplete': 'family-name',
            'required': 'required',
        }),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'jane.doe@example.com',
            'autocomplete': 'email',
            'required': 'required',
        }),
    )
    phone = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '+1 (555) 000-0000',
            'autocomplete': 'tel',
        }),
    )
    address = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '123 Market Street, Apt 4B',
            'autocomplete': 'street-address',
            'required': 'required',
        }),
    )
    city = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'San Francisco',
            'autocomplete': 'address-level2',
            'required': 'required',
        }),
    )
    postal_code = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '94105',
            'autocomplete': 'postal-code',
            'required': 'required',
        }),
    )
    country = forms.CharField(
        max_length=100,
        required=True,
        initial='United States',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'United States',
            'autocomplete': 'country-name',
            'required': 'required',
        }),
    )

    class Meta:
        model = Order
        fields = (
            'first_name',
            'last_name',
            'email',
            'phone',
            'address',
            'city',
            'postal_code',
            'country',
        )
