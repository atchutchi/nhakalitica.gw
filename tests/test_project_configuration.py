import os
import subprocess
import sys
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

    def test_production_stack_serves_static_files_behind_https_proxy(self):
        self.assertIn(
            "whitenoise.middleware.WhiteNoiseMiddleware",
            settings.MIDDLEWARE,
        )
        self.assertEqual(
            getattr(settings, "SECURE_PROXY_SSL_HEADER", None),
            ("HTTP_X_FORWARDED_PROTO", "https"),
        )

    def test_database_url_selects_postgresql(self):
        environment = os.environ.copy()
        environment.update(
            {
                "DJANGO_SETTINGS_MODULE": "config.settings",
                "DEBUG": "True",
                "DATABASE_URL": "postgresql://kalitica:secret@postgres.internal:5432/kalitica",
            }
        )
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "from django.conf import settings; print(settings.DATABASES['default']['ENGINE'])",
            ],
            cwd=settings.BASE_DIR,
            env=environment,
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertEqual(result.stdout.strip(), "django.db.backends.postgresql")

    def test_railway_public_domain_is_trusted_automatically(self):
        environment = os.environ.copy()
        environment.update(
            {
                "DJANGO_SETTINGS_MODULE": "config.settings",
                "DEBUG": "True",
                "RAILWAY_PUBLIC_DOMAIN": "nha-kalitica-demo.up.railway.app",
            }
        )
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "from django.conf import settings; "
                    "print(settings.ALLOWED_HOSTS.count('nha-kalitica-demo.up.railway.app')); "
                    "print(settings.ALLOWED_HOSTS.count('healthcheck.railway.app')); "
                    "print(settings.CSRF_TRUSTED_ORIGINS[-1] if settings.CSRF_TRUSTED_ORIGINS else ''); "
                    "print(settings.PUBLIC_BASE_URL)"
                ),
            ],
            cwd=settings.BASE_DIR,
            env=environment,
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertEqual(
            result.stdout.splitlines(),
            [
                "1",
                "1",
                "https://nha-kalitica-demo.up.railway.app",
                "https://nha-kalitica-demo.up.railway.app",
            ],
        )

    def test_railway_volume_becomes_media_root(self):
        environment = os.environ.copy()
        environment.update(
            {
                "DJANGO_SETTINGS_MODULE": "config.settings",
                "DEBUG": "True",
                "RAILWAY_VOLUME_MOUNT_PATH": "/app/media",
            }
        )
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "from django.conf import settings; print(settings.MEDIA_ROOT.as_posix())",
            ],
            cwd=settings.BASE_DIR,
            env=environment,
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertEqual(result.stdout.strip(), "/app/media")

    def test_demo_seed_command_is_registered(self):
        from django.core.management import get_commands

        self.assertIn("seed_demo_accounts", get_commands())

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
