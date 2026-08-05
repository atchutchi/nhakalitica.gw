import tomllib

from django.conf import settings
from django.test import TestCase, override_settings


class RailwayConfigurationTests(TestCase):
    def test_railway_healthcheck_hostname_is_allowed(self):
        self.assertIn("healthcheck.railway.app", settings.ALLOWED_HOSTS)

    @override_settings(SECURE_SSL_REDIRECT=True)
    def test_healthcheck_accepts_railway_internal_http_request(self):
        response = self.client.get("/saude/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_predeploy_uses_single_railway_command(self):
        config = tomllib.loads((settings.BASE_DIR / "railway.toml").read_text(encoding="utf-8"))

        commands = config["deploy"]["preDeployCommand"]
        self.assertEqual(len(commands), 1)
        self.assertIn("manage.py migrate", commands[0])
        self.assertIn("manage.py seed_demo_accounts", commands[0])
