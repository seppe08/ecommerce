from django import forms


class CartAddProductForm(forms.Form):
    """
    Form for validating and adding a product to the cart.
    """
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-input qty-input',
            'min': '1',
            'value': '1',
            'aria-label': 'Product quantity',
        }),
    )
    override = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput,
    )
