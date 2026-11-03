from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class FoodListing(models.Model):

    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        UNAVAILABLE = "unavailable", "Unavailable"

    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="food_listings"
    )

    title = models.CharField(max_length=200)

    category = models.CharField(max_length=100)

    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    location = models.CharField(max_length=255)

    collection_deadline = models.DateTimeField()

    description = models.TextField(
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )


    def clean(self):
        super().clean()

        if self.donor_id is not None and self.donor.role != "DONOR":
            raise ValidationError({
                "donor": "Only users with the Donor role can own food listings."
            })

        if self.collection_deadline and self.collection_deadline <= timezone.now():
            raise ValidationError({
                "collection_deadline": "Collection deadline must be in the future."
            })


    def __str__(self):
        return self.title