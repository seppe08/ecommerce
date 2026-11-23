from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    """
    Accessible customer review form capturing rating, headline, and feedback.
    """

    rating = forms.ChoiceField(
        choices=Review.RATING_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select w-full rounded-control border border-line bg-surface px-3 py-2 text-ink"
            }
        ),
        initial=5,
    )
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={
                "class": "form-input w-full rounded-control border border-line bg-surface px-3 py-2 text-ink",
                "placeholder": "Headline for your review (e.g. Outstanding quality!)",
                "required": "required",
            }
        ),
    )
    comment = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-input w-full rounded-control border border-line bg-surface px-3 py-2 text-ink",
                "rows": 4,
                "placeholder": "What did you love or think could be improved about this product?",
                "required": "required",
            }
        ),
    )

    class Meta:
        model = Review
        fields = ("rating", "title", "comment")
