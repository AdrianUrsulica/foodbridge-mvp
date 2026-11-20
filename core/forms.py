
from django import forms
from django.utils import timezone

from .models import FoodListing


class FoodListingForm(forms.ModelForm):

    class Meta:
        model = FoodListing

        fields = [
            "title",
            "category",
            "quantity",
            "location",
            "collection_deadline",
            "description",
        ]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Fresh Bread",
            }),
            "category": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Bakery",
            }),
            "quantity": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
            }),
            "location": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Collection location",
            }),
            "collection_deadline": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                },
                format="%Y-%m-%dT%H:%M",
            ),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Optional description",
            }),
        }

    collection_deadline = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            attrs={
                "type": "datetime-local",
                "class": "form-control",
            },
            format="%Y-%m-%dT%H:%M",
        ),
    )

    def clean_collection_deadline(self):
        deadline = self.cleaned_data["collection_deadline"]

        if deadline <= timezone.now():
            raise forms.ValidationError(
                "Collection deadline must be in the future."
            )

        return deadline
