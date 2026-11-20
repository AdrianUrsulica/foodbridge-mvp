from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import FoodListing


class ViewFoodListingsTests(TestCase):

    def setUp(self):
        User = get_user_model()
        self.donor = User.objects.create_user(
            username="donor1", email="donor1@example.com",
            password="TestPassword123!", role="DONOR"
        )
        self.recipient = User.objects.create_user(
            username="recipient1", email="recipient1@example.com",
            password="TestPassword123!", role="RECIPIENT"
        )
        self.client.force_login(self.recipient)

    def make_listing(self, title, days_left=1, status=FoodListing.Status.AVAILABLE):
        return FoodListing.objects.create(
            donor=self.donor,
            title=title,
            category="Bakery",
            quantity=15,
            location="Wembley, London",
            collection_deadline=timezone.now() + timedelta(days=days_left),
            status=status,
        )

    # AC1: users can access the food listings page
    def test_listings_page_loads(self):
        response = self.client.get(reverse("food_listings"))
        self.assertEqual(response.status_code, 200)

    # AC2 and AC3: available listings are shown with their details
    def test_available_listing_is_shown_with_details(self):
        self.make_listing("Fresh Bread")
        response = self.client.get(reverse("food_listings"))
        self.assertContains(response, "Fresh Bread")
        self.assertContains(response, "Bakery")
        self.assertContains(response, "15")
        self.assertContains(response, "Wembley, London")
        self.assertContains(response, "Collect by")

    # AC4: expired listings are hidden
    def test_expired_listing_is_not_shown(self):
        self.make_listing("Old Sandwiches", days_left=-1)
        response = self.client.get(reverse("food_listings"))
        self.assertNotContains(response, "Old Sandwiches")

    # AC4: unavailable listings are hidden
    def test_unavailable_listing_is_not_shown(self):
        self.make_listing("Taken Soup", status=FoodListing.Status.UNAVAILABLE)
        response = self.client.get(reverse("food_listings"))
        self.assertNotContains(response, "Taken Soup")

    # AC5: a clear message when nothing is available
    def test_empty_message_when_no_listings(self):
        response = self.client.get(reverse("food_listings"))
        self.assertContains(response, "No food listings are available right now.")

    # AC7: the page is linked from the navigation
    def test_navigation_links_to_listings_page(self):
        response = self.client.get(reverse("recipient_home"))
        self.assertContains(response, reverse("food_listings"))

    # Only signed-in users can see the page
    def test_logged_out_user_is_sent_to_login(self):
        self.client.logout()
        response = self.client.get(reverse("food_listings"))
        self.assertRedirects(
            response, reverse("login") + "?next=" + reverse("food_listings")
        )