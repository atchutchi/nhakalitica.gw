from django.contrib.auth import get_user_model
from django.test import TestCase

from memberships.models import Membership
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

    def test_private_organization_data_is_not_in_snapshot_without_consent(self):
        user = get_user_model().objects.create_user(
            email="private-organization@example.com",
            password="PalavraPasseSegura2026!",
        )
        membership = user.membership
        membership.status = Membership.Status.APPROVED
        membership.represents_organization = True
        membership.organization_name = "Organização Teste"
        membership.organization_role = "Representante"
        membership.organization_purpose = "Procurar talento"
        membership.save()

        payload = user.profile.build_public_snapshot()

        self.assertNotIn("organization_name", payload)
        self.assertNotIn("organization_role", payload)
        self.assertNotIn("organization_purpose", payload)

    def test_organization_name_and_role_enter_snapshot_only_with_consent(self):
        user = get_user_model().objects.create_user(
            email="public-organization@example.com",
            password="PalavraPasseSegura2026!",
        )
        membership = user.membership
        membership.status = Membership.Status.APPROVED
        membership.represents_organization = True
        membership.organization_name = "Organização Teste"
        membership.organization_role = "Representante"
        membership.organization_purpose = "Procurar talento"
        membership.save()
        user.profile.show_organization_on_profile = True
        user.profile.save(update_fields=("show_organization_on_profile",))

        payload = user.profile.build_public_snapshot()

        self.assertEqual(payload["organization_name"], "Organização Teste")
        self.assertEqual(payload["organization_role"], "Representante")
        self.assertNotIn("organization_purpose", payload)

    def test_unapproved_representative_cannot_publish_organization(self):
        user = get_user_model().objects.create_user(
            email="unapproved-organization@example.com",
            password="PalavraPasseSegura2026!",
        )
        membership = user.membership
        membership.represents_organization = True
        membership.organization_name = "Organização Privada"
        membership.organization_role = "Representante"
        membership.save()
        user.profile.show_organization_on_profile = True
        user.profile.save(update_fields=("show_organization_on_profile",))

        payload = user.profile.build_public_snapshot()

        self.assertNotIn("organization_name", payload)
        self.assertNotIn("organization_role", payload)
