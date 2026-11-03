from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


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

    def __str__(self):
        return self.title