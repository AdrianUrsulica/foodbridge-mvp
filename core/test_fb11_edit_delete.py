from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from core.models import FoodListing


class EditDeleteFoodListingTests(TestCase):

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

    def setUp(self):
        self.deadline = timezone.now() + timedelta(days=2)
        self.listing = FoodListing.objects.create(
            donor=self.donor,
            title="Fresh Bread",
            category="Bakery",
            quantity=10,
            location="Wembley, London",
            collection_deadline=self.deadline,
        )
        self.edit_url = reverse("edit_food_listing", args=[self.listing.pk])
        self.delete_url = reverse("delete_food_listing", args=[self.listing.pk])
        self.mine_url = reverse("my_food_listings")

    def valid_data(self, **changes):
        data = {
            "title": "Fresh Bread",
            "category": "Bakery",
            "quantity": 10,
            "location": "Wembley, London",
            "collection_deadline": self.deadline.strftime("%Y-%m-%dT%H:%M"),
            "description": "",
        }
        data.update(changes)
        return data

    # AC1 / AC2: the owner can edit, and changes are saved

    def test_owner_can_open_edit_page(self):
        self.client.force_login(self.donor)
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/edit_food_listing.html")
        self.assertContains(response, "Fresh Bread")

    def test_owner_can_edit_listing(self):
        self.client.force_login(self.donor)
        response = self.client.post(
            self.edit_url,
            self.valid_data(title="Brown Bread", quantity=5),
        )
        self.assertRedirects(response, self.mine_url)
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.title, "Brown Bread")
        self.assertEqual(self.listing.quantity, 5)
        self.assertEqual(self.listing.donor, self.donor)

    # AC7: invalid changes are rejected with validation messages

    def test_edit_rejects_missing_title(self):
        self.client.force_login(self.donor)
        response = self.client.post(self.edit_url, self.valid_data(title=""))
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "title", "This field is required."
        )
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.title, "Fresh Bread")

    def test_edit_rejects_zero_quantity(self):
        self.client.force_login(self.donor)
        response = self.client.post(self.edit_url, self.valid_data(quantity=0))
        self.assertEqual(response.status_code, 200)
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.quantity, 10)

    def test_edit_rejects_past_deadline(self):
        self.client.force_login(self.donor)
        past = (timezone.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")
        response = self.client.post(
            self.edit_url, self.valid_data(collection_deadline=past)
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Collection deadline must be in the future.")
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.collection_deadline, self.deadline)

    # AC3 / AC4: the owner can delete, after a confirmation step

    def test_delete_get_shows_confirmation_without_deleting(self):
        self.client.force_login(self.donor)
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/delete_food_listing.html")
        self.assertContains(response, "Fresh Bread")
        self.assertTrue(FoodListing.objects.filter(pk=self.listing.pk).exists())

    def test_owner_can_delete_listing(self):
        self.client.force_login(self.donor)
        response = self.client.post(self.delete_url)
        self.assertRedirects(response, self.mine_url)
        self.assertFalse(FoodListing.objects.filter(pk=self.listing.pk).exists())

    # AC5: another Donor cannot edit or delete

    def test_other_donor_cannot_open_edit_page(self):
        self.client.force_login(self.other_donor)
        self.assertEqual(self.client.get(self.edit_url).status_code, 404)

    def test_other_donor_cannot_edit_listing(self):
        self.client.force_login(self.other_donor)
        response = self.client.post(self.edit_url, self.valid_data(title="Hacked"))
        self.assertEqual(response.status_code, 404)
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.title, "Fresh Bread")

    def test_other_donor_cannot_delete_listing(self):
        self.client.force_login(self.other_donor)
        self.assertEqual(self.client.post(self.delete_url).status_code, 404)
        self.assertTrue(FoodListing.objects.filter(pk=self.listing.pk).exists())

    def test_recipient_cannot_edit_or_delete(self):
        self.client.force_login(self.recipient)
        self.assertEqual(self.client.get(self.edit_url).status_code, 404)
        self.assertEqual(self.client.post(self.delete_url).status_code, 404)
        self.assertTrue(FoodListing.objects.filter(pk=self.listing.pk).exists())

    def test_missing_listing_returns_404(self):
        self.client.force_login(self.donor)
        url = reverse("edit_food_listing", args=[99999])
        self.assertEqual(self.client.get(url).status_code, 404)

    # AC6: logged-out users cannot reach edit or delete

    def test_anonymous_user_redirected_from_edit(self):
        response = self.client.post(self.edit_url, self.valid_data(title="Hacked"))
        self.assertRedirects(response, reverse("login") + "?next=" + self.edit_url)
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.title, "Fresh Bread")

    def test_anonymous_user_redirected_from_delete(self):
        response = self.client.post(self.delete_url)
        self.assertRedirects(response, reverse("login") + "?next=" + self.delete_url)
        self.assertTrue(FoodListing.objects.filter(pk=self.listing.pk).exists())

    # Navigation: "My Food Listings" shows only the Donor's own listings

    def test_my_listings_shows_only_own_listings_with_controls(self):
        FoodListing.objects.create(
            donor=self.other_donor,
            title="Other Donor Apples",
            category="Fruit",
            quantity=3,
            location="Harrow",
            collection_deadline=self.deadline,
        )
        self.client.force_login(self.donor)
        response = self.client.get(self.mine_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Fresh Bread")
        self.assertContains(response, f'href="{self.edit_url}"')
        self.assertContains(response, f'href="{self.delete_url}"')
        self.assertNotContains(response, "Other Donor Apples")

    def test_recipient_cannot_open_my_listings(self):
        self.client.force_login(self.recipient)
        self.assertEqual(self.client.get(self.mine_url).status_code, 403)

    def test_donor_home_links_to_my_listings(self):
        self.client.force_login(self.donor)
        response = self.client.get(reverse("donor_home"))
        self.assertContains(response, f'href="{self.mine_url}"')

    def test_success_message_shown_after_delete(self):
        self.client.force_login(self.donor)
        response = self.client.post(self.delete_url, follow=True)
        self.assertContains(response, "&quot;Fresh Bread&quot; was deleted.")
