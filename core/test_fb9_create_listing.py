
from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from core.models import FoodListing


class CreateFoodListingTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.donor = User.objects.create_user(
            username="testdonor",
            email="testdonor@example.com",
            password="TestPassword123!",
            role=User.Role.DONOR,
        )

        cls.recipient = User.objects.create_user(
            username="testrecipient",
            email="testrecipient@example.com",
            password="TestPassword123!",
            role=User.Role.RECIPIENT,
        )

    def setUp(self):
        self.url = reverse("create_food_listing")

        self.valid_data = {
            "title": "Fresh Bread",
            "category": "Bakery",
            "quantity": 10,
            "location": "London",
            "collection_deadline": (
                timezone.now() + timedelta(days=5)
            ).strftime("%Y-%m-%dT%H:%M"),
            "description": "Fresh bread for collection.",
        }

    def test_donor_can_access_create_page(self):
        self.client.force_login(self.donor)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "core/create_food_listing.html"
        )

    def test_recipient_cannot_create_listing(self):
        self.client.force_login(self.recipient)

        response = self.client.post(
            self.url, self.valid_data
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(FoodListing.objects.count(), 0)

    def test_anonymous_user_redirected_to_login(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_valid_listing_is_saved(self):
        self.client.force_login(self.donor)

        response = self.client.post(
            self.url, self.valid_data
        )

        self.assertEqual(FoodListing.objects.count(), 1)
        self.assertRedirects(
            response, reverse("food_listings")
)

    def test_listing_assigned_to_logged_in_donor(self):
        self.client.force_login(self.donor)

        self.client.post(self.url, self.valid_data)

        listing = FoodListing.objects.get()

        self.assertEqual(listing.donor, self.donor)
        self.assertEqual(
            listing.status, FoodListing.Status.AVAILABLE
        )

    def test_zero_quantity_is_rejected(self):
        self.client.force_login(self.donor)

        data = self.valid_data.copy()
        data["quantity"] = 0

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(FoodListing.objects.count(), 0)
        self.assertFormError(
            response.context["form"],
            "quantity",
            "Ensure this value is greater than or equal to 1."
        )

    def test_past_deadline_is_rejected(self):
        self.client.force_login(self.donor)

        data = self.valid_data.copy()
        data["collection_deadline"] = (
            timezone.now() - timedelta(days=1)
        ).strftime("%Y-%m-%dT%H:%M")

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(FoodListing.objects.count(), 0)
        self.assertFormError(
            response.context["form"],
            "collection_deadline",
            "Collection deadline must be in the future."
        )

    def test_missing_title_is_rejected(self):
        self.client.force_login(self.donor)

        data = self.valid_data.copy()
        data["title"] = ""

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(FoodListing.objects.count(), 0)
        self.assertFormError(
            response.context["form"],
            "title",
            "This field is required."
        )

    def test_description_is_optional(self):
        self.client.force_login(self.donor)

        data = self.valid_data.copy()
        data["description"] = ""

        self.client.post(self.url, data)

        self.assertEqual(FoodListing.objects.count(), 1)
