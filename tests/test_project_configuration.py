import os
from pathlib import Path
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
            "Kalitica Networking Society <noreply@nhakalitica.gw>",
        )
        self.assertIn("memberships", settings.INSTALLED_APPS)

    def test_project_uses_expected_directories_and_user_model(self):
        self.assertEqual(settings.AUTH_USER_MODEL, "accounts.User")
        self.assertIn(settings.BASE_DIR / "templates", settings.TEMPLATES[0]["DIRS"])
        self.assertIn(settings.BASE_DIR / "static", settings.STATICFILES_DIRS)
        self.assertEqual(settings.MEDIA_ROOT, settings.BASE_DIR / "media")

    def test_source_has_no_encoding_artifacts(self):
        suspicious = (
            chr(0xFFFD),
            "".join(chr(value) for value in (0x00E2, 0x20AC, 0x2122)),
            "?" * 2,
            *(
                chr(0x00C3) + chr(second)
                for second in (0x00A0, 0x00A1, 0x00A2, 0x00A3, 0x00A7, 0x00A9, 0x00AD, 0x00B3, 0x00B5)
            ),
        )
        roots = ("accounts", "config", "core", "interactions", "memberships", "moderation", "profiles", "taxonomy", "templates")
        failures = []
        for root in roots:
            for path in (settings.BASE_DIR / root).rglob("*"):
                if path.suffix not in {".py", ".html"} or "migrations" in path.parts:
                    continue
                if path.name in {"text_encoding.py", "test_encoding.py"}:
                    continue
                text = path.read_text(encoding="utf-8")
                if any(marker in text for marker in suspicious):
                    failures.append(str(path.relative_to(settings.BASE_DIR)))
        self.assertEqual(failures, [])

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
