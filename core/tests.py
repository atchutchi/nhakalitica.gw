from pathlib import Path

from django.conf import settings
from django.test import Client, TestCase, override_settings
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

    @override_settings(PUBLIC_SIGNUP_ENABLED=False)
    def test_closed_signup_is_announced_before_the_hero_actions(self):
        response = self.client.get(reverse("home"))
        html = response.content.decode()

        self.assertContains(response, "Registos temporariamente encerrados")
        self.assertLess(
            html.index("Registos temporariamente encerrados"),
            html.index('class="hero-network-actions"'),
        )
        self.assertNotContains(response, ">Pedir adesão<")

    def test_public_menu_exposes_translated_open_and_close_labels(self):
        response = self.client.get(reverse("home"))

        self.assertContains(response, 'data-open-label="Abrir menu"')
        self.assertContains(response, 'data-close-label="Fechar menu"')


class BrandedErrorPageTests(TestCase):
    def test_permission_denied_uses_the_kalitica_error_page(self):
        user = get_user_model().objects.create_user(
            email="sem-permissao@example.com", password="test-pass"
        )
        self.client.force_login(user)

        response = self.client.get(reverse("moderation:dashboard"))

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Não tens permissão para aceder a esta página", status_code=403)
        self.assertContains(response, "Kalitica Networking Society", status_code=403)
        self.assertContains(response, reverse("accounts:dashboard"), status_code=403)

    def test_expired_form_uses_the_kalitica_csrf_page(self):
        csrf_client = Client(enforce_csrf_checks=True)

        response = csrf_client.post(reverse("accounts:logout"))

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "O formulário expirou", status_code=403)
        self.assertContains(response, "Actualizar e tentar novamente", status_code=403)
        self.assertNotContains(response, "CSRF", status_code=403)


class PublicVisualContractTests(TestCase):
    def test_public_brand_assets_are_not_clipped_and_hero_mark_is_prominent(self):
        public_css = (Path(settings.BASE_DIR) / "static" / "css" / "public.css").read_text(
            encoding="utf-8"
        )

        self.assertIn(".public-brand {", public_css)
        self.assertIn("overflow: visible;", public_css)
        self.assertIn("transform: none;", public_css)
        self.assertIn("width: clamp(680px, 58vw, 760px);", public_css)

    def test_home_uses_kalitica_public_shell(self):
        response = self.client.get(reverse("home"))

        self.assertContains(response, "A rede profissional da Guiné-Bissau")
        self.assertContains(response, 'class="public-header"')
        self.assertContains(response, 'class="hero-network"')
        self.assertContains(response, reverse("accounts:signup"))
        self.assertNotContains(response, "CVLink")
        self.assertNotContains(response, "10€/mês")

    def test_navy_information_card_has_explicit_heading_contrast(self):
        public_css = (Path(settings.BASE_DIR) / "static" / "css" / "public.css").read_text(
            encoding="utf-8"
        )

        self.assertIn(".public-info-card-navy h2", public_css)
        self.assertIn("color: #fff;", public_css)

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

    def test_public_copy_uses_consistent_european_portuguese(self):
        about_response = self.client.get(reverse("about"))
        membership_response = self.client.get(reverse("membership-types"))
        login_response = self.client.get(reverse("accounts:login"))
        reset_response = self.client.get(reverse("accounts:password_reset"))

        self.assertContains(about_response, "ligações significativas")
        self.assertContains(about_response, "Ligamos profissionais")
        self.assertContains(membership_response, "Todas as adesões estão sujeitas")
        self.assertContains(login_response, "Esqueceste-te da palavra-passe?")
        self.assertContains(reset_response, "Lembraste-te da palavra-passe?")


class LegalPageTests(TestCase):
    def select_language(self, language, next_url):
        response = self.client.post(
            "/i18n/setlang/",
            {"language": language, "next": next_url},
        )
        self.assertRedirects(response, next_url)

    def test_legal_pages_are_public_versioned_and_canonical(self):
        expected = {
            "/termos/": "Termos de Utilização",
            "/privacidade/": "Política de Privacidade",
            "/codigo-de-conduta/": "Código de Conduta",
        }

        for path, heading in expected.items():
            with self.subTest(path=path):
                response = self.client.get(path)

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, heading)
                self.assertContains(response, "Versão 1.0")
                self.assertContains(response, "5 de Agosto de 2026")
                self.assertContains(response, "info@nhakalitica.gw")
                self.assertContains(response, 'rel="canonical"')

    @override_settings(PUBLIC_BASE_URL="https://nhakalitica.gw")
    def test_legal_canonical_uses_the_configured_public_domain(self):
        response = self.client.get(reverse("privacy"))

        self.assertContains(
            response,
            '<link rel="canonical" href="https://nhakalitica.gw/privacidade/">',
            html=True,
        )

    def test_legal_pages_are_available_in_english(self):
        self.select_language("en", "/privacidade/")

        self.assertContains(self.client.get("/termos/"), "Terms of Use")
        self.assertContains(self.client.get("/privacidade/"), "Privacy Policy")
        self.assertContains(self.client.get("/codigo-de-conduta/"), "Code of Conduct")
        self.assertContains(
            self.client.get("/privacidade/"),
            "the account is deactivated for 30 days",
        )
        self.assertContains(
            self.client.get("/codigo-de-conduta/"),
            "Respect members’ visibility choices",
        )

    def test_legal_pages_are_available_in_french(self):
        self.select_language("fr", "/privacidade/")

        self.assertContains(self.client.get("/termos/"), "Conditions d’utilisation")
        self.assertContains(self.client.get("/privacidade/"), "Politique de confidentialité")
        self.assertContains(self.client.get("/codigo-de-conduta/"), "Code de conduite")
        self.assertContains(
            self.client.get("/privacidade/"),
            "le compte est désactivé pendant 30 jours",
        )
        self.assertContains(
            self.client.get("/codigo-de-conduta/"),
            "Respecte les choix de visibilité des membres",
        )

    def test_public_footer_links_to_legal_pages_and_official_contact(self):
        response = self.client.get("/")

        self.assertContains(response, 'href="/termos/"')
        self.assertContains(response, 'href="/privacidade/"')
        self.assertContains(response, 'href="/codigo-de-conduta/"')
        self.assertContains(response, 'href="mailto:info@nhakalitica.gw"')
        self.assertNotContains(response, "info@kalitica.org")

    def test_signup_links_the_documents_the_user_accepts(self):
        response = self.client.get(reverse("accounts:signup"))

        self.assertContains(response, 'href="/termos/"')
        self.assertContains(response, 'href="/privacidade/"')


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
        self.assertContains(response, reverse("terms"))
        self.assertContains(response, reverse("privacy"))
        self.assertContains(response, reverse("code-of-conduct"))
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


class InterfaceLanguageTests(TestCase):
    def select_language(self, language, next_url="/"):
        response = self.client.post(
            "/i18n/setlang/",
            {"language": language, "next": next_url},
        )
        self.assertRedirects(response, next_url)

    def test_french_public_home_translates_content_and_document_language(self):
        self.select_language("fr")

        response = self.client.get("/")

        self.assertContains(response, '<html lang="fr">')
        self.assertContains(response, "Le réseau professionnel")
        self.assertContains(response, "Demander l’adhésion")

    def test_header_and_footer_language_controls_use_the_locale_endpoint(self):
        response = self.client.get("/")

        self.assertContains(response, 'action="/i18n/setlang/"', count=6)

    def test_english_login_translates_content_and_document_language(self):
        self.select_language("en", "/conta/entrar/")

        response = self.client.get("/conta/entrar/")

        self.assertContains(response, '<html lang="en">')
        self.assertContains(response, "Welcome back to Kalitica.")
        self.assertContains(response, ">Sign in<")

    def test_english_authentication_copy_is_natural(self):
        self.select_language("en", "/conta/entrar/")

        login_response = self.client.get("/conta/entrar/")
        reset_response = self.client.get("/conta/recuperar-palavra-passe/")

        self.assertContains(login_response, "Don't have an account yet?")
        self.assertContains(reset_response, "Remember your password?")

    def test_language_selection_persists_across_pages(self):
        self.select_language("fr")

        home_response = self.client.get("/")
        login_response = self.client.get("/conta/entrar/")

        self.assertContains(home_response, "Comment ça marche")
        self.assertContains(login_response, "Bienvenue à nouveau chez Kalitica.")

    def test_public_information_and_signup_are_available_in_english(self):
        self.select_language("en")

        about_response = self.client.get("/sobre/")
        membership_response = self.client.get("/tipos-de-adesao/")
        signup_response = self.client.get("/conta/criar/")

        self.assertContains(about_response, "Our mission")
        self.assertContains(membership_response, "Every application is reviewed")
        self.assertContains(signup_response, "Country of residence")

    def test_member_journeys_use_the_selected_language(self):
        user = get_user_model().objects.create_user(
            email="language-member@example.com",
            password="PalavraPasseSegura2026!",
        )
        self.client.force_login(user)
        self.select_language("en", "/adesao/")

        application_response = self.client.get("/adesao/")

        self.assertContains(application_response, "My application")
        self.assertContains(application_response, "Continue application")

        user.membership.status = Membership.Status.APPROVED
        user.membership.save(update_fields=("status",))
        directory_response = self.client.get("/pesquisar/")

        self.assertContains(directory_response, "Search professionals")
        self.assertContains(directory_response, "Apply filters")
        self.assertContains(directory_response, 'action="/i18n/setlang/"', count=1)
        self.assertContains(directory_response, 'name="language" value="pt"')
        self.assertContains(directory_response, 'name="language" value="fr"')
        self.assertContains(directory_response, 'name="language" value="en"')
