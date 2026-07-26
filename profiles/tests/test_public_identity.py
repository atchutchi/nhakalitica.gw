from django.contrib.auth import get_user_model
from django.test import TestCase

from taxonomy.models import Skill


class PublicProfileIdentityTests(TestCase):
    def test_profile_receives_unique_slug(self):
        first = get_user_model().objects.create_user(
            email="maria1@example.com",
            password="PalavraPasseSegura2026!",
            first_name="Maria",
            last_name="Sambu",
        )
        second = get_user_model().objects.create_user(
            email="maria2@example.com",
            password="PalavraPasseSegura2026!",
            first_name="Maria",
            last_name="Sambu",
        )

        self.assertTrue(first.profile.slug.startswith("maria-sambu"))
        self.assertTrue(second.profile.slug.startswith("maria-sambu"))
        self.assertNotEqual(first.profile.slug, second.profile.slug)

    def test_slug_does_not_change_with_public_name(self):
        user = get_user_model().objects.create_user(
            email="joao@example.com",
            password="PalavraPasseSegura2026!",
            first_name="João",
            last_name="Mendes",
        )
        original_slug = user.profile.slug

        user.profile.public_name = "João da Silva Mendes"
        user.profile.save()

        self.assertEqual(user.profile.slug, original_slug)

    def test_public_country_is_hidden_when_location_is_private(self):
        user = get_user_model().objects.create_user(
            email="localizacao-privada@example.com", password="PalavraPasseSegura2026!"
        )
        user.profile.country = "Guiné-Bissau"
        user.profile.location_is_public = False
        user.profile.save(update_fields=("country", "location_is_public"))

        self.assertEqual(user.profile.public_country, "")

    def test_incomplete_published_snapshot_never_uses_current_profile_values(self):
        user = get_user_model().objects.create_user(
            email="snapshot-incompleto@example.com", password="PalavraPasseSegura2026!"
        )
        profile = user.profile
        profile.public_name = "Nome actual secreto"
        profile.professional_title = "Titulo actual secreto"
        profile.location = "Cidade actual secreta"
        profile.country = "Pais actual secreto"
        profile.location_is_public = True
        profile.published_snapshot = {"public_name": "Nome aprovado"}
        profile.save()
        secret_skill = Skill.objects.create(name="Competencia actual secreta", slug="competencia-actual-secreta")
        profile.skills.add(secret_skill)

        self.assertEqual(profile.public_display_name, "Nome aprovado")
        self.assertEqual(profile.public_professional_title, "")
        self.assertEqual(profile.public_location, "")
        self.assertEqual(profile.public_country, "")
        self.assertEqual(profile.public_skill_names, [])
