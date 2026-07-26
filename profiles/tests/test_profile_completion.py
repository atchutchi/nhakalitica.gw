from django.contrib.auth import get_user_model
from django.test import TestCase

from profiles.models import Education, Experience, ProfileLanguage
from taxonomy.models import Area, Sector, Skill, Specialization


class ProfileCompletionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="perfil@example.com",
            password="PalavraPasseSegura2026!",
        )

    def test_empty_profile_reports_required_sections(self):
        profile = self.user.profile

        self.assertEqual(profile.completion_percentage, 0)
        self.assertCountEqual(
            profile.missing_required_sections(),
            [
                "nome público",
                "título profissional",
                "biografia",
                "localização",
                "especialização",
                "competência",
                "experiência",
                "formação",
                "idioma",
            ],
        )

    def test_complete_profile_reaches_one_hundred_percent(self):
        profile = self.user.profile
        profile.public_name = "Maria Sambu"
        profile.professional_title = "Programadora Django"
        profile.bio = "Profissional com experiência em aplicações web e serviços públicos digitais."
        profile.location = "Bissau"
        profile.save()
        sector = Sector.objects.create(name="Tecnologia", slug="tecnologia")
        area = Area.objects.create(sector=sector, name="Software", slug="software")
        specialization = Specialization.objects.create(area=area, name="Web", slug="web")
        skill = Skill.objects.create(name="Django", slug="django")
        profile.specializations.add(specialization)
        profile.skills.add(skill)
        Experience.objects.create(
            profile=profile,
            title="Programadora",
            organization="Organização",
            start_date="2024-01-01",
            is_current=True,
        )
        Education.objects.create(
            profile=profile,
            institution="Universidade",
            qualification="Licenciatura",
            field_of_study="Informática",
            start_date="2020-01-01",
            end_date="2023-12-31",
        )
        ProfileLanguage.objects.create(profile=profile, name="Português", level="fluent")

        self.assertEqual(profile.completion_percentage, 100)
        self.assertEqual(profile.missing_required_sections(), [])
        self.assertTrue(profile.can_submit)
