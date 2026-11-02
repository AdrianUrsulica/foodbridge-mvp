"""FB-7 authentication tests (Sprint 1).

Adds coverage for cases the existing tests do not check: missing fields,
password rules, anonymous access, wrong-role redirects and logout rules.
Each test name maps to a scenario in features/authentication.feature.
Run with:  python manage.py test accounts
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()

PASSWORD = "StrongPass123!"


def make_user(username, role, email=None):
    return User.objects.create_user(
        username=username,
        email=email or f"{username}@example.com",
        role=role,
        password=PASSWORD,
    )


def register_data(**overrides):
    data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "role": "DONOR",
        "password1": PASSWORD,
        "password2": PASSWORD,
    }
    data.update(overrides)
    return data


class RegistrationValidationTests(TestCase):
    """FB-2: required fields, password rules, duplicates."""

    def test_missing_email_is_rejected(self):
        response = self.client.post(reverse("register"), register_data(email=""))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="newuser").exists())

    def test_missing_role_is_rejected(self):
        response = self.client.post(reverse("register"), register_data(role=""))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="newuser").exists())

    def test_invalid_role_is_rejected(self):
        response = self.client.post(reverse("register"), register_data(role="ADMIN"))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="newuser").exists())

    def test_mismatched_passwords_are_rejected(self):
        response = self.client.post(
            reverse("register"), register_data(password2="DifferentPass456!")
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="newuser").exists())

    def test_too_short_password_is_rejected(self):
        response = self.client.post(
            reverse("register"), register_data(password1="Ab1!", password2="Ab1!")
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="newuser").exists())

    def test_numeric_only_password_is_rejected(self):
        response = self.client.post(
            reverse("register"),
            register_data(password1="48392016574", password2="48392016574"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="newuser").exists())

    def test_duplicate_username_is_rejected(self):
        make_user("newuser", "DONOR", email="other@example.com")
        response = self.client.post(reverse("register"), register_data())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username="newuser").count(), 1)

    def test_successful_registration_redirects_to_role_area(self):
        response = self.client.post(
            reverse("register"), register_data(username="d1", email="d1@example.com")
        )
        self.assertRedirects(
            response, reverse("role_home"), fetch_redirect_response=False
        )

    def test_password_is_stored_hashed(self):
        self.client.post(reverse("register"), register_data())
        user = User.objects.get(username="newuser")
        self.assertNotEqual(user.password, PASSWORD)
        self.assertTrue(user.check_password(PASSWORD))

    def test_logged_in_user_is_redirected_away_from_register(self):
        make_user("donor1", "DONOR")
        self.client.login(username="donor1", password=PASSWORD)
        response = self.client.get(reverse("register"))
        self.assertRedirects(
            response, reverse("role_home"), fetch_redirect_response=False
        )


class LoginTests(TestCase):
    """FB-3: valid and invalid credentials, redirects."""

    def setUp(self):
        make_user("donor1", "DONOR")
        make_user("charity1", "RECIPIENT")

    def test_donor_login_redirects_to_donor_area(self):
        response = self.client.post(
            reverse("login"), {"username": "donor1", "password": PASSWORD}, follow=True
        )
        self.assertEqual(response.redirect_chain[-1][0], reverse("donor_home"))

    def test_recipient_login_redirects_to_recipient_area(self):
        response = self.client.post(
            reverse("login"),
            {"username": "charity1", "password": PASSWORD},
            follow=True,
        )
        self.assertEqual(response.redirect_chain[-1][0], reverse("recipient_home"))

    def test_wrong_password_shows_error_and_does_not_log_in(self):
        response = self.client.post(
            reverse("login"), {"username": "donor1", "password": "WrongPass999!"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_unknown_user_does_not_log_in(self):
        response = self.client.post(
            reverse("login"), {"username": "nobody", "password": PASSWORD}
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_empty_credentials_do_not_log_in(self):
        response = self.client.post(reverse("login"), {"username": "", "password": ""})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_page_loads_for_anonymous_user(self):
        self.assertEqual(self.client.get(reverse("login")).status_code, 200)


class ProtectedPageTests(TestCase):
    """FB-3 / FB-4: unauthenticated users cannot reach protected pages."""

    def test_anonymous_user_is_sent_to_login(self):
        for name in ("role_home", "donor_home", "recipient_home"):
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 302)
                self.assertTrue(response.url.startswith(reverse("login")))


class RoleAccessTests(TestCase):
    """FB-4: each role is kept to its own area."""

    def setUp(self):
        make_user("donor1", "DONOR")
        make_user("charity1", "RECIPIENT")

    def test_donor_can_open_donor_page(self):
        self.client.login(username="donor1", password=PASSWORD)
        self.assertEqual(self.client.get(reverse("donor_home")).status_code, 200)

    def test_recipient_can_open_recipient_page(self):
        self.client.login(username="charity1", password=PASSWORD)
        self.assertEqual(self.client.get(reverse("recipient_home")).status_code, 200)

    def test_recipient_is_kept_out_of_donor_page(self):
        self.client.login(username="charity1", password=PASSWORD)
        response = self.client.get(reverse("donor_home"))
        self.assertRedirects(
            response, reverse("recipient_home"), fetch_redirect_response=False
        )

    def test_donor_is_kept_out_of_recipient_page(self):
        self.client.login(username="donor1", password=PASSWORD)
        response = self.client.get(reverse("recipient_home"))
        self.assertRedirects(
            response, reverse("donor_home"), fetch_redirect_response=False
        )

    def test_role_home_sends_each_role_to_its_area(self):
        self.client.login(username="donor1", password=PASSWORD)
        self.assertRedirects(
            self.client.get(reverse("role_home")),
            reverse("donor_home"),
            fetch_redirect_response=False,
        )
        self.client.logout()
        self.client.login(username="charity1", password=PASSWORD)
        self.assertRedirects(
            self.client.get(reverse("role_home")),
            reverse("recipient_home"),
            fetch_redirect_response=False,
        )

    def test_user_with_no_role_is_sent_to_login(self):
        User.objects.create_user(username="norole", email="n@example.com", password=PASSWORD)
        self.client.login(username="norole", password=PASSWORD)
        response = self.client.get(reverse("role_home"))
        self.assertRedirects(
            response, reverse("login"), fetch_redirect_response=False
        )


class LogoutTests(TestCase):
    """FB-5: logout ends the session and protects pages afterwards."""

    def setUp(self):
        make_user("donor1", "DONOR")
        self.client.login(username="donor1", password=PASSWORD)

    def test_logout_ends_session_and_redirects_to_login(self):
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("login"), fetch_redirect_response=False)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_protected_page_is_blocked_after_logout(self):
        self.client.post(reverse("logout"))
        response = self.client.get(reverse("donor_home"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("login")))

    def test_logout_requires_post(self):
        # Django 5+ rejects GET logout. Records the real behaviour.
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 405)
        self.assertIn("_auth_user_id", self.client.session)
