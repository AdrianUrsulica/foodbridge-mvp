from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class RegistrationTests(TestCase):
    def test_donor_can_register(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "donor1",
                "email": "donor@example.com",
                "role": "DONOR",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="donor1")
        self.assertEqual(user.role, "DONOR")

    def test_recipient_can_register(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "charity1",
                "email": "charity@example.com",
                "role": "RECIPIENT",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="charity1")
        self.assertEqual(user.role, "RECIPIENT")

    def test_duplicate_email_is_rejected(self):
        User.objects.create_user(
            username="first",
            email="same@example.com",
            role="DONOR",
            password="StrongPass123!",
        )
        response = self.client.post(
            reverse("register"),
            {
                "username": "second",
                "email": "same@example.com",
                "role": "RECIPIENT",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            User.objects.filter(email="same@example.com").count(),
            1,
        )