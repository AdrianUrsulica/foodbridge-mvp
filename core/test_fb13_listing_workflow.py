"""FB-13 Sprint 2 acceptance tests.

These tests check the surplus food listing features from FB-8 to FB-12
working together, end to end, the way a Donor and a Recipient would use them.
Each feature also has its own tests in core/tests.py and core/test_fb9_*,
test_fb10_* and test_fb11_* files.
"""
from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from core.models import FoodListing


def form_deadline(days):
    """Return a deadline in the format the datetime-local form field expects."""
    return (timezone.now() + timedelta(days=days)).strftime("%Y-%m-%dT%H:%M")


class SprintTwoListingWorkflowTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.donor = User.objects.create_user(
            username="donor1",
            email="donor1@example.com",
            password="TestPassword123!",
            role=User.Role.DONOR,
        )
        cls.other_donor = User.objects.create_user(
            username="donor2",
            email="donor2@example.com",
            password="TestPassword123!",
            role=User.Role.DONOR,
        )
        cls.recipient = User.objects.create_user(
            username="recipient1",
            email="recipient1@example.com",
            password="TestPassword123!",
            role=User.Role.RECIPIENT,
        )

    def listing_data(self, **changes):
        data = {
            "title": "Fresh Bread",
            "category": "Bakery",
            "quantity": 10,
            "location": "Wembley, London",
            "collection_deadline": form_deadline(2),
            "description": "Fresh bread for collection.",
        }
        data.update(changes)
        return data

    def make_listing(self, donor, title, days_left=2):
        return FoodListing.objects.create(
            donor=donor,
            title=title,
            category="Bakery",
            quantity=5,
            location="Harrow",
            collection_deadline=timezone.now() + timedelta(days=days_left),
        )

    def listings_page_as_recipient(self):
        self.client.force_login(self.recipient)
        return self.client.get(reverse("food_listings"))

    # Full workflow: create -> view -> edit -> view -> delete -> view

    def test_full_listing_lifecycle(self):
        # Donor creates a listing (FB-9)
        self.client.force_login(self.donor)
        self.client.post(reverse("create_food_listing"), self.listing_data())
        listing = FoodListing.objects.get(title="Fresh Bread")
        self.assertEqual(listing.donor, self.donor)

        # Recipient can see it on the available listings page (FB-10)
        self.assertContains(self.listings_page_as_recipient(), "Fresh Bread")

        # Donor edits it (FB-11)
        self.client.force_login(self.donor)
        self.client.post(
            reverse("edit_food_listing", args=[listing.pk]),
            self.listing_data(title="Brown Bread", quantity=4),
        )

        # Recipient now sees the updated listing, not the old one
        response = self.listings_page_as_recipient()
        self.assertContains(response, "Brown Bread")
        self.assertNotContains(response, "Fresh Bread")

        # Donor deletes it (FB-11)
        self.client.force_login(self.donor)
        self.client.post(reverse("delete_food_listing", args=[listing.pk]))

        # It is gone for the Recipient and from the database
        self.assertNotContains(self.listings_page_as_recipient(), "Brown Bread")
        self.assertFalse(FoodListing.objects.filter(pk=listing.pk).exists())

    # Several Donors: each sees and manages only their own listings

    def test_recipient_sees_listings_from_all_donors(self):
        self.make_listing(self.donor, "Fresh Bread")
        self.make_listing(self.other_donor, "Apples")
        response = self.listings_page_as_recipient()
        self.assertContains(response, "Fresh Bread")
        self.assertContains(response, "Apples")

    def test_my_listings_only_shows_each_donors_own_listings(self):
        self.make_listing(self.donor, "Fresh Bread")
        self.make_listing(self.other_donor, "Apples")

        self.client.force_login(self.other_donor)
        response = self.client.get(reverse("my_food_listings"))
        self.assertContains(response, "Apples")
        self.assertNotContains(response, "Fresh Bread")

    def test_other_donors_listing_is_unchanged_after_failed_edit_and_delete(self):
        listing = self.make_listing(self.donor, "Fresh Bread")
        self.client.force_login(self.other_donor)

        self.client.post(
            reverse("edit_food_listing", args=[listing.pk]),
            self.listing_data(title="Hacked"),
        )
        self.client.post(reverse("delete_food_listing", args=[listing.pk]))

        listing.refresh_from_db()
        self.assertEqual(listing.title, "Fresh Bread")
        self.assertContains(self.listings_page_as_recipient(), "Fresh Bread")

    # Expired listings: hidden from Recipients, still manageable by the owner

    def test_expired_listing_hidden_from_recipient_but_shown_to_owner(self):
        listing = self.make_listing(self.donor, "Old Soup", days_left=-1)

        self.assertNotContains(self.listings_page_as_recipient(), "Old Soup")

        self.client.force_login(self.donor)
        response = self.client.get(reverse("my_food_listings"))
        self.assertContains(response, "Old Soup")
        self.assertContains(
            response, reverse("delete_food_listing", args=[listing.pk])
        )

    def test_owner_can_delete_expired_listing(self):
        listing = self.make_listing(self.donor, "Old Soup", days_left=-1)
        self.client.force_login(self.donor)
        self.client.post(reverse("delete_food_listing", args=[listing.pk]))
        self.assertFalse(FoodListing.objects.filter(pk=listing.pk).exists())

    def test_expired_listing_reappears_after_owner_sets_new_deadline(self):
        listing = self.make_listing(self.donor, "Old Soup", days_left=-1)
        self.client.force_login(self.donor)
        self.client.post(
            reverse("edit_food_listing", args=[listing.pk]),
            self.listing_data(title="Old Soup", collection_deadline=form_deadline(3)),
        )
        self.assertContains(self.listings_page_as_recipient(), "Old Soup")

    # Validation is the same when creating and when editing (FB-12)

    def test_invalid_data_rejected_on_both_create_and_edit(self):
        listing = self.make_listing(self.donor, "Fresh Bread")
        self.client.force_login(self.donor)
        bad_inputs = [
            {"title": ""},
            {"quantity": 0},
            {"location": ""},
            {"collection_deadline": form_deadline(-1)},
        ]
        for bad in bad_inputs:
            with self.subTest(bad=bad):
                create = self.client.post(
                    reverse("create_food_listing"), self.listing_data(**bad)
                )
                edit = self.client.post(
                    reverse("edit_food_listing", args=[listing.pk]),
                    self.listing_data(**bad),
                )
                self.assertEqual(create.status_code, 200)
                self.assertEqual(edit.status_code, 200)

        self.assertEqual(FoodListing.objects.count(), 1)
        listing.refresh_from_db()
        self.assertEqual(listing.title, "Fresh Bread")
        self.assertEqual(listing.quantity, 5)

    # Access control across every listing page (FB-12)

    def test_logged_out_user_is_sent_to_login_from_every_listing_page(self):
        listing = self.make_listing(self.donor, "Fresh Bread")
        urls = [
            reverse("food_listings"),
            reverse("create_food_listing"),
            reverse("my_food_listings"),
            reverse("edit_food_listing", args=[listing.pk]),
            reverse("delete_food_listing", args=[listing.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, reverse("login") + "?next=" + url)

    def test_recipient_cannot_use_any_donor_page(self):
        listing = self.make_listing(self.donor, "Fresh Bread")
        self.client.force_login(self.recipient)
        self.assertEqual(self.client.get(reverse("create_food_listing")).status_code, 403)
        self.assertEqual(self.client.get(reverse("my_food_listings")).status_code, 403)
        self.assertEqual(
            self.client.get(reverse("edit_food_listing", args=[listing.pk])).status_code,
            404,
        )
        self.assertEqual(
            self.client.post(reverse("delete_food_listing", args=[listing.pk])).status_code,
            404,
        )
        self.assertTrue(FoodListing.objects.filter(pk=listing.pk).exists())
