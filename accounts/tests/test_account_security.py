import re

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class AccountSecurityTests(TestCase):
    def tearDown(self):
        cache.clear()

    def test_signup_sends_single_use_confirmation_link(self):
        self.client.post(
            reverse("accounts:signup"),
            {
                "email": "nova@example.com",
                "first_name": "Nova",
                "last_name": "Pessoa",
                "password1": "PalavraPasseSegura2026!",
                "password2": "PalavraPasseSegura2026!",
            },
        )
        user = get_user_model().objects.get(email="nova@example.com")
        self.assertIsNone(user.email_verified_at)
        self.assertEqual(len(mail.outbox), 1)
        path = re.search(r"http://testserver(/conta/confirmar-email/[^\s]+)", mail.outbox[0].body).group(1)

        response = self.client.get(path)
        self.assertRedirects(response, reverse("accounts:dashboard"))
        user.refresh_from_db()
        self.assertIsNotNone(user.email_verified_at)

        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "foi utilizada")

    def test_password_reset_does_not_reveal_unknown_email(self):
        response = self.client.post(reverse("accounts:password_reset"), {"email": "unknown@example.com"})
        self.assertRedirects(response, reverse("accounts:password_reset_done"))
        self.assertEqual(len(mail.outbox), 0)

    def test_user_can_edit_account_details(self):
        user = get_user_model().objects.create_user(email="old@example.com", password="test-pass")
        self.client.force_login(user)

        response = self.client.post(
            reverse("accounts:edit"),
            {"email": "new@example.com", "first_name": "Novo", "last_name": "Nome"},
        )
        self.assertRedirects(response, reverse("accounts:dashboard"))
        user.refresh_from_db()
        self.assertEqual(user.email, "new@example.com")
        self.assertIsNone(user.email_verified_at)

    def test_deactivation_requires_correct_password(self):
        user = get_user_model().objects.create_user(email="user@example.com", password="correct-pass")
        self.client.force_login(user)

        response = self.client.post(reverse("accounts:deactivate"), {"password": "wrong-pass"})
        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

        response = self.client.post(reverse("accounts:deactivate"), {"password": "correct-pass"})
        self.assertRedirects(response, reverse("accounts:login"))
        user.refresh_from_db()
        self.assertFalse(user.is_active)
        self.assertFalse(user.profile.is_public)

    def test_repeated_failed_login_is_temporarily_limited(self):
        get_user_model().objects.create_user(email="login@example.com", password="correct-pass")
        for _index in range(5):
            self.client.post(
                reverse("accounts:login"),
                {"username": "login@example.com", "password": "wrong-pass"},
                REMOTE_ADDR="192.0.2.10",
            )

        response = self.client.post(
            reverse("accounts:login"),
            {"username": "login@example.com", "password": "correct-pass"},
            REMOTE_ADDR="192.0.2.10",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Demasiadas tentativas")
