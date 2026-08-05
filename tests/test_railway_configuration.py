import tomllib

from django.conf import settings
from django.test import SimpleTestCase


class RailwayConfigurationTests(SimpleTestCase):
    def test_predeploy_uses_single_railway_command(self):
        config = tomllib.loads((settings.BASE_DIR / "railway.toml").read_text(encoding="utf-8"))

        commands = config["deploy"]["preDeployCommand"]
        self.assertEqual(len(commands), 1)
        self.assertIn("manage.py migrate", commands[0])
        self.assertIn("manage.py seed_demo_accounts", commands[0])
