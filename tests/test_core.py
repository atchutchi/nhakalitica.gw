from django.test import TestCase
from django.urls import reverse


class PublicFooterTests(TestCase):
    def test_public_footer_has_institutional_groups_and_bottom_line(self):
        response = self.client.get(reverse("home"))

        self.assertContains(response, 'class="public-footer-grid"')
        self.assertContains(response, 'class="public-footer-nav"')
        self.assertContains(response, 'class="public-footer-meta"')
        self.assertContains(response, 'class="public-footer-bottom"')
        self.assertContains(response, "Informação legal")
        self.assertContains(response, "Contacto e idiomas")
        self.assertContains(response, "Todos os direitos reservados.")
