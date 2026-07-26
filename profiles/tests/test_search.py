import tempfile

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.test import TestCase, override_settings

from profiles.models import Profile
from taxonomy.models import Area, Sector, Skill, Specialization


class PublicSearchTests(TestCase):
    def setUp(self):
        self.sector = Sector.objects.create(name="Tecnologia", slug="tecnologia")
        self.area = Area.objects.create(
            sector=self.sector,
            name="Desenvolvimento de software",
            slug="desenvolvimento-software",
        )
        self.specialization = Specialization.objects.create(
            area=self.area,
            name="Desenvolvimento Web",
            slug="desenvolvimento-web",
        )
        self.skill = Skill.objects.create(name="Django", slug="django")
        self.skill.specializations.add(self.specialization)
        self.public_profile = self.create_profile(
            "maria@example.com",
            "Maria Sambu",
            "Programadora Django",
            approved=True,
        )
        self.private_profile = self.create_profile(
            "privado@example.com",
            "Perfil Privado",
            "Programador Django",
            approved=False,
        )

    def create_profile(self, email, name, title, approved):
        user = get_user_model().objects.create_user(email=email, password="Segura2026!")
        profile = user.profile
        profile.public_name = name
        profile.professional_title = title
        profile.bio = "Experiência em projetos digitais e desenvolvimento web."
        profile.location = "Bissau"
        profile.phone = "+245 000 0000"
        profile.status = Profile.Status.APPROVED if approved else Profile.Status.DRAFT
        profile.is_public = approved
        profile.save()
        profile.specializations.add(self.specialization)
        profile.skills.add(self.skill)
        return profile

    def test_search_returns_only_approved_public_profiles(self):
        response = self.client.get("/pesquisar/", {"q": "Django"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Maria Sambu")
        self.assertNotContains(response, "Perfil Privado")

    def test_search_filters_by_skill_and_location(self):
        response = self.client.get(
            "/pesquisar/",
            {"skill": self.skill.slug, "location": "Bissau"},
        )

        self.assertContains(response, "Maria Sambu")

    def test_private_location_is_hidden_and_not_searchable(self):
        self.public_profile.location_is_public = False
        self.public_profile.save()

        detail = self.client.get(f"/profissionais/{self.public_profile.slug}/")
        search = self.client.get("/pesquisar/", {"location": "Bissau"})
        search_by_text = self.client.get("/pesquisar/", {"q": "Bissau cidade"})

        self.assertNotContains(detail, "Bissau")
        self.assertNotContains(search, "Maria Sambu")
        self.assertNotContains(search_by_text, "Maria Sambu")

    def test_cv_download_respects_visibility_and_disables_indexing(self):
        with tempfile.TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            self.public_profile.cv_file.save("curriculo.pdf", ContentFile(b"%PDF-1.4\nteste"))
            self.public_profile.cv_visibility = Profile.CVVisibility.PRIVATE
            self.public_profile.save()
            url = f"/profissionais/{self.public_profile.slug}/curriculo/"

            self.assertEqual(self.client.get(url).status_code, 404)
            self.public_profile.cv_visibility = Profile.CVVisibility.MEMBERS
            self.public_profile.save()
            self.assertEqual(self.client.get(url).status_code, 404)
            member = get_user_model().objects.create_user(email="member@example.com", password="test-pass")
            self.client.force_login(member)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response["X-Robots-Tag"], "noindex, nofollow, noarchive")
            response.close()

    def test_public_profile_hides_private_contacts(self):
        response = self.client.get(f"/profissionais/{self.public_profile.slug}/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Maria Sambu")
        self.assertNotContains(response, self.public_profile.user.email)
        self.assertNotContains(response, self.public_profile.phone)

    def test_private_profile_returns_not_found(self):
        response = self.client.get(f"/profissionais/{self.private_profile.slug}/")

        self.assertEqual(response.status_code, 404)

    def test_search_uses_approved_snapshot_during_pending_changes(self):
        profile = self.public_profile
        profile.published_snapshot = profile.build_public_snapshot()
        approved_title = profile.professional_title
        profile.professional_title = "Título ainda não aprovado"
        profile.status = Profile.Status.CHANGES_PENDING
        profile.save()

        approved_response = self.client.get("/pesquisar/", {"q": approved_title})
        pending_response = self.client.get("/pesquisar/", {"q": "ainda não aprovado"})

        self.assertContains(approved_response, profile.public_display_name)
        self.assertNotContains(pending_response, profile.public_display_name)

    def test_search_is_accent_insensitive_and_includes_profile_sections(self):
        profile = self.public_profile
        profile.professional_title = "Técnica de Comunicação"
        profile.bio = "Gestão de relações públicas e comunicação institucional."
        profile.save()
        profile.experiences.create(
            title="Gestora de projectos",
            organization="CVLink",
            description="Coordenação de equipas",
            start_date="2022-01-01",
        )

        response = self.client.get("/pesquisar/", {"q": "comunicacao"})
        self.assertContains(response, profile.public_name)
        response = self.client.get("/pesquisar/", {"q": "coordenacao"})
        self.assertContains(response, profile.public_name)

    def test_search_uses_role_synonyms_without_short_term_false_positives(self):
        technical = self.public_profile
        technical.professional_title = "Fullstack Developer e IT Project Manager"
        technical.target_roles = "Programador, engenheiro de software, gestor de projectos tecnológicos"
        technical.search_keywords = "software, desenvolvimento web, programação, tecnologia de informação"
        technical.save()
        communication = self.create_profile(
            "comunicacao@example.com",
            "Ana Comunicação",
            "Assessora de comunicação institucional",
            approved=True,
        )
        communication.bio = "Comunicação institucional e relações públicas."
        communication.skills.clear()
        communication.specializations.clear()
        communication.save()

        software_response = self.client.get("/pesquisar/", {"q": "software"})
        ti_response = self.client.get("/pesquisar/", {"q": "ti"})

        self.assertContains(software_response, technical.public_name)
        self.assertNotContains(software_response, communication.public_name)
        self.assertContains(ti_response, technical.public_name)
        self.assertNotContains(ti_response, communication.public_name)

    def test_project_and_projeto_spellings_find_the_same_profile(self):
        profile = self.public_profile
        profile.bio = "Gestão de projectos digitais e coordenação de equipas."
        profile.search_keywords = "gestão de projetos, coordenação de projetos"
        profile.save()

        old_spelling = self.client.get("/pesquisar/", {"q": "projectos"})
        current_spelling = self.client.get("/pesquisar/", {"q": "projetos"})

        self.assertContains(old_spelling, profile.public_name)
        self.assertContains(current_spelling, profile.public_name)

    def test_search_keywords_support_recruiter_function_terms(self):
        profile = self.public_profile
        profile.professional_title = "Gestora operacional"
        profile.target_roles = "Analista de dados, consultora de reporting"
        profile.search_keywords = "business intelligence, dashboards, Power BI"
        profile.save()

        response = self.client.get("/pesquisar/", {"q": "business intelligence"})

        self.assertContains(response, profile.public_name)

    def test_location_filter_is_accent_insensitive(self):
        self.public_profile.location = "São Vicente"
        self.public_profile.save()

        response = self.client.get("/pesquisar/", {"location": "Sao Vicente"})

        self.assertContains(response, self.public_profile.public_name)

    def test_filters_match_the_approved_snapshot_after_pending_changes(self):
        profile = self.public_profile
        profile.published_snapshot = profile.build_public_snapshot()
        profile.status = Profile.Status.CHANGES_PENDING
        profile.save()

        response = self.client.get("/pesquisar/", {"specialization": self.specialization.slug})
        self.assertContains(response, profile.public_name)
        response = self.client.get("/pesquisar/", {"skill": self.skill.slug})
        self.assertContains(response, profile.public_name)

    def test_language_and_city_aliases_are_supported(self):
        self.public_profile.languages.create(name="Português", level="fluent")
        response = self.client.get("/pesquisar/", {"idioma": "portugues", "cidade": "Bissau"})
        self.assertContains(response, self.public_profile.public_name)

    def test_area_page_lists_only_public_professionals(self):
        response = self.client.get(f"/areas/{self.area.slug}/")

        self.assertContains(response, "Maria Sambu")
        self.assertNotContains(response, "Perfil Privado")

    def test_experience_filter_uses_public_dates_without_error(self):
        self.public_profile.experiences.create(
            title="Responsável técnico",
            organization="CVLink",
            description="Projetos",
            start_date="2018-01-01",
            end_date="2023-01-01",
        )
        response = self.client.get("/pesquisar/", {"experience": "3"})
        self.assertContains(response, self.public_profile.public_name)

    def test_country_filter_respects_private_location(self):
        self.public_profile.country = "Guiné-Bissau"
        self.public_profile.location_is_public = False
        self.public_profile.save()
        response = self.client.get("/pesquisar/", {"country": "Guiné"})
        self.assertNotContains(response, self.public_profile.public_name)

    def test_active_filters_are_rendered_as_removable_tags(self):
        response = self.client.get(
            "/pesquisar/",
            {"q": "django", "skill": self.skill.slug, "experience": "3"},
        )
        self.assertContains(response, "Pesquisa: django")
        self.assertContains(response, "Competência: Django")
        self.assertContains(response, "Experiência mínima: 3")
        self.assertContains(response, "Remover filtro Competência: Django")
