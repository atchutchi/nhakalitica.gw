from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from profiles.models import Profile
from memberships.models import Membership
from taxonomy.models import Area, Sector

from .features import FEATURES, active_features, locked_features


class HomeViewTests(TestCase):
    def test_home_page_is_public(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A rede profissional da Guiné-Bissau")

    def test_home_page_is_available_for_authenticated_users(self):
        user = get_user_model().objects.create_user(email="home@example.com", password="test-pass")
        self.client.force_login(user)
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A rede profissional da Guiné-Bissau")

    def test_login_page_does_not_render_global_header(self):
        response = self.client.get(reverse("accounts:login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bem-vindo de volta à Kalitica")
        self.assertNotContains(response, 'class="site-header"')


class PublicVisualContractTests(TestCase):
    def test_home_uses_kalitica_public_shell(self):
        response = self.client.get(reverse("home"))

        self.assertContains(response, "A rede profissional da Guiné-Bissau")
        self.assertContains(response, 'class="public-header"')
        self.assertContains(response, 'class="hero-network"')
        self.assertContains(response, reverse("accounts:signup"))
        self.assertNotContains(response, "CVLink")
        self.assertNotContains(response, "10€/mês")

    def test_institutional_pages_use_public_navigation(self):
        for route_name, heading in (
            ("about", "A nossa missão"),
            ("membership-types", "Tipos de adesão"),
            ("how-it-works", "Como funciona a adesão"),
        ):
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, heading)
                self.assertContains(response, 'class="public-header"')

    def test_public_page_has_three_language_controls(self):
        response = self.client.get(reverse("home"))

        self.assertContains(response, 'value="pt"')
        self.assertContains(response, 'value="fr"')
        self.assertContains(response, 'value="en"')


class SeoAndOperationsTests(TestCase):
    def setUp(self):
        sector = Sector.objects.create(name="Tecnologia", slug="tecnologia")
        self.area = Area.objects.create(sector=sector, name="Software", slug="software")
        owner = get_user_model().objects.create_user(email="seo@example.com", password="test-pass")
        membership = owner.membership
        membership.member_type = Membership.Type.EFFECTIVE
        membership.relationship = Membership.Relationship.CITIZEN
        membership.status = Membership.Status.APPROVED
        membership.save()
        self.profile = owner.profile
        self.profile.public_name = "Pessoa Pública"
        self.profile.professional_title = "Programadora"
        self.profile.status = Profile.Status.APPROVED
        self.profile.is_public = True
        self.profile.review_status = Profile.ReviewStatus.APPROVED
        self.profile.is_discoverable = True
        self.profile.save()

    def test_sitemap_excludes_private_profiles_and_areas(self):
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("about"))
        self.assertContains(response, reverse("membership-types"))
        self.assertContains(response, reverse("how-it-works"))
        self.assertNotContains(response, f"/profissionais/{self.profile.slug}/")
        self.assertNotContains(response, f"/areas/{self.area.slug}/")

    def test_robots_blocks_private_sections_and_links_sitemap(self):
        response = self.client.get("/robots.txt")
        self.assertContains(response, "Disallow: /conta/")
        self.assertContains(response, "/sitemap.xml")

    def test_public_profile_has_canonical_open_graph_and_structured_data(self):
        self.client.force_login(self.profile.user)
        response = self.client.get(f"/profissionais/{self.profile.slug}/")
        self.assertContains(response, 'rel="canonical"')
        self.assertContains(response, 'property="og:title"')
        self.assertContains(response, '"@type": "Person"')

    def test_search_and_dashboard_are_not_indexed(self):
        self.client.force_login(self.profile.user)
        self.assertContains(self.client.get("/pesquisar/"), 'content="noindex,nofollow"')
        self.assertContains(self.client.get("/conta/painel/"), 'content="noindex,nofollow"')

    def test_health_endpoint_reports_success(self):
        response = self.client.get("/saude/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_home_page_presents_product_and_search(self):
        response = self.client.get("/")

        self.assertContains(response, "Guiné-Bissau")
        self.assertContains(response, "diáspora")
        self.assertContains(response, "kalitica-logo.png")
        self.assertContains(response, "/conta/criar/")
        self.assertContains(response, "/conta/entrar/")
        self.assertNotContains(response, "Europa")
        self.assertNotContains(response, "europeu")

    def test_future_features_are_structured_but_locked(self):
        self.assertEqual([feature.key for feature in active_features()], ["talent_repository"])
        self.assertIn("jobs", FEATURES)
        self.assertIn("teams", FEATURES)
        self.assertIn("billing", FEATURES)
        self.assertTrue(all(not feature.public_enabled for feature in locked_features()))

        response = self.client.get("/")
        self.assertNotContains(response, "Planos e cobranças")

    def test_home_page_declares_brand_favicon(self):
        response = self.client.get("/")

        self.assertContains(response, 'rel="icon"')
