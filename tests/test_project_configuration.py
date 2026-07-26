import os
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from config.settings import get_secret_key


class KaliticaConfigurationTests(SimpleTestCase):
    def test_project_identity_and_locale(self):
        self.assertEqual(settings.LANGUAGE_CODE, "pt")
        self.assertEqual(settings.TIME_ZONE, "Africa/Bissau")
        self.assertEqual(
            settings.DEFAULT_FROM_EMAIL,
            "Kalitica <noreply@nhakalitica.gw>",
        )
        self.assertIn("memberships", settings.INSTALLED_APPS)

    def test_project_uses_expected_directories_and_user_model(self):
        self.assertEqual(settings.AUTH_USER_MODEL, "accounts.User")
        self.assertIn(settings.BASE_DIR / "templates", settings.TEMPLATES[0]["DIRS"])
        self.assertIn(settings.BASE_DIR / "static", settings.STATICFILES_DIRS)

    @patch.dict(os.environ, {}, clear=True)
    def test_development_can_use_local_secret_key(self):
        self.assertEqual(get_secret_key(debug=True), "development-only-secret-key")

    @patch.dict(os.environ, {}, clear=True)
    def test_production_requires_explicit_secret_key(self):
        with self.assertRaisesMessage(
            ImproperlyConfigured,
            "SECRET_KEY é obrigatória quando DEBUG=False.",
        ):
            get_secret_key(debug=False)

    @patch.dict(os.environ, {"SECRET_KEY": "uma-chave-segura-de-producao"}, clear=True)
    def test_production_uses_configured_secret_key(self):
        self.assertEqual(get_secret_key(debug=False), "uma-chave-segura-de-producao")


class BrandNeutralizationTests(TestCase):
    def test_home_uses_kalitica_identity(self):
        response = self.client.get(reverse("home"), follow=True)

        self.assertContains(response, "Kalitica")
        self.assertNotContains(response, "CVLink")

    def test_authenticated_home_has_no_cvlink_identity(self):
        user = get_user_model().objects.create_user(
            email="member@example.com",
            password="safe-password-123",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("home"))

        self.assertContains(response, "Kalitica")
        self.assertNotContains(response, "CVLink")
