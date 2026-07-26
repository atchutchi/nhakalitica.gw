from django.conf import settings
from django.test import SimpleTestCase


class DomainAppConfigurationTests(SimpleTestCase):
    def test_domain_apps_are_installed(self):
        self.assertIn("taxonomy", settings.INSTALLED_APPS)
        self.assertIn("profiles", settings.INSTALLED_APPS)
