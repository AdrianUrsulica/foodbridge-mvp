
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class LoginLogoutTests(TestCase):

    def setUp(self):
        self.donor = User.objects.create_user(
            username="testdonor",
            email="testdonor@example.com",
            password="StrongPass123!",
            role="DONOR"
        )

        self.recipient = User.objects.create_user(
            username="testrecipient",
            email="testrecipient@example.com",
            password="StrongPass123!",
            role="RECIPIENT"
        )

    def test_valid_donor_login(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "testdonor",
                "password": "StrongPass123!"
            }
        )

        self.assertRedirects(
            response,
            reverse("role_home"),
            fetch_redirect_response=False
        )

        self.assertTrue(
            self.client.session.get("_auth_user_id")
        )

    def test_valid_recipient_login(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "testrecipient",
                "password": "StrongPass123!"
            }
        )

        self.assertEqual(response.status_code, 302)

        self.assertTrue(
            self.client.session.get("_auth_user_id")
        )

    def test_invalid_login(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "testdonor",
                "password": "WrongPassword123!"
            }
        )

        self.assertEqual(response.status_code, 200)

        self.assertFalse(
            response.wsgi_request.user.is_authenticated
        )

        self.assertContains(
            response,
            "Invalid username or password."
        )

    def test_logout(self):
        self.client.login(
            username="testdonor",
            password="StrongPass123!"
        )

        response = self.client.post(
            reverse("logout")
        )

        self.assertRedirects(
            response,
            reverse("login")
        )

        self.assertNotIn(
            "_auth_user_id",
            self.client.session
        )

    def test_protected_page_after_logout(self):
        self.client.login(
            username="testdonor",
            password="StrongPass123!"
        )

        self.client.post(reverse("logout"))

        response = self.client.get(
            reverse("donor_home")
        )

        self.assertEqual(response.status_code, 302)

        self.assertIn(
            reverse("login"),
            response.url
        )
