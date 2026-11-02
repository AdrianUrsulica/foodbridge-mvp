from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from .models import FoodListing


class FoodListingModelTests(TestCase):

    def setUp(self):
        self.donor = get_user_model().objects.create_user(
            username="testdonor",
            email="donor@example.com",
            password="TestPassword123!",
            role="DONOR"
        )

    def test_food_listing_creation(self):
        listing = FoodListing.objects.create(
            donor=self.donor,
            title="Fresh Bread",
            category="Bakery",
            quantity=15,
            location="Wembley, London",
            collection_deadline=timezone.now() + timedelta(days=1),
            description="Fresh bread available for collection."
        )

        self.assertEqual(listing.title, "Fresh Bread")
        self.assertEqual(listing.donor, self.donor)
        self.assertEqual(listing.quantity, 15)
        self.assertEqual(
            listing.status,
            FoodListing.Status.AVAILABLE
        )

    def test_food_listing_rejects_zero_quantity(self):
        listing = FoodListing(
            donor=self.donor,
            title="Fresh Bread",
            category="Bakery",
            quantity=0,
            location="Wembley, London",
            collection_deadline=timezone.now() + timedelta(days=1)
        )

        with self.assertRaises(ValidationError):
            listing.full_clean()

    def test_food_listing_requires_title(self):
        listing = FoodListing(
            donor=self.donor,
            title="",
            category="Bakery",
            quantity=15,
            location="Wembley, London",
            collection_deadline=timezone.now() + timedelta(days=1)
        )

        with self.assertRaises(ValidationError):
            listing.full_clean()