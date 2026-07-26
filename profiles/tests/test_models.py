from django.contrib.auth import get_user_model
from django.test import TestCase

from profiles.models import Profile
from taxonomy.models import Area, Sector, Skill, Specialization


class ProfileModelTests(TestCase):
    def test_creating_user_creates_private_draft_profile(self):
        user = get_user_model().objects.create_user(
            email="maria@example.com",
            password="PalavraPasseSegura2026!",
            first_name="Maria",
            last_name="Sambu",
        )

        profile = user.profile

        self.assertEqual(profile.public_name, "Maria Sambu")
        self.assertEqual(profile.status, Profile.Status.DRAFT)
        self.assertFalse(profile.is_public)

    def test_profile_accepts_specializations_and_skills(self):
        user = get_user_model().objects.create_user(
            email="joao@example.com",
            password="PalavraPasseSegura2026!",
        )
        sector = Sector.objects.create(name="Tecnologia", slug="tecnologia")
        area = Area.objects.create(sector=sector, name="Software", slug="software")
        specialization = Specialization.objects.create(
            area=area,
            name="Web",
            slug="web",
        )
        skill = Skill.objects.create(name="Django", slug="django")

        user.profile.specializations.add(specialization)
        user.profile.skills.add(skill)

        self.assertEqual(list(user.profile.specializations.all()), [specialization])
        self.assertEqual(list(user.profile.skills.all()), [skill])

    def test_profile_defines_all_moderation_states(self):
        self.assertEqual(
            {choice for choice, _label in Profile.Status.choices},
            {
                "draft",
                "pending",
                "approved",
                "rejected",
                "changes_pending",
                "suspended",
                "archived",
                "deleted",
            },
        )
