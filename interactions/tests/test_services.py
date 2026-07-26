from django.contrib.auth import get_user_model
from django.test import TestCase

from interactions.models import Favorite, RecruitmentTag
from interactions.services import (
    build_shortlist_csv,
    clean_saved_search_params,
    get_comparable_favorites,
    sync_favorite_tags,
)
from profiles.models import Profile


class ShortlistServiceTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(email="recrutador@example.com", password="test-pass")
        self.other_user = user_model.objects.create_user(email="outro@example.com", password="test-pass")
        self.owner = user_model.objects.create_user(email="profissional@example.com", password="test-pass")
        self.profile = self.owner.profile
        self.profile.public_name = "Profissional Público"
        self.profile.professional_title = "Engenheira Civil"
        self.profile.status = Profile.Status.APPROVED
        self.profile.is_public = True
        self.profile.save()
        self.favorite = Favorite.objects.create(user=self.user, profile=self.profile)

    def test_sync_favorite_tags_creates_unique_tags_in_input_order(self):
        tags = sync_favorite_tags(self.favorite, "Civil, urgente, civil")

        self.assertEqual([tag.name for tag in tags], ["Civil", "urgente"])
        self.assertEqual(self.favorite.tags.count(), 2)

    def test_clean_saved_search_params_keeps_only_non_empty_allowed_values(self):
        cleaned = clean_saved_search_params(
            {"q": "engenheiro", "unsafe": "x", "experience": "5", "location": ""}
        )

        self.assertEqual(cleaned, {"q": "engenheiro", "experience": "5"})

    def test_get_comparable_favorites_returns_only_owned_public_favorites(self):
        owned = get_comparable_favorites(self.user, [self.profile.pk])

        self.assertEqual(list(owned), [self.favorite])
        self.assertEqual(list(get_comparable_favorites(self.other_user, [self.profile.pk])), [])

    def test_build_shortlist_csv_hides_private_candidate_data_and_escapes_notes(self):
        self.profile.phone = "+245000"
        self.profile.whatsapp = "+245111"
        self.profile.location = "Rua privada"
        self.profile.country = "Guiné-Bissau"
        self.profile.location_is_public = False
        self.profile.save()
        self.favorite.notes = "=ligar"
        self.favorite.save()

        csv_text = build_shortlist_csv(self.user, Favorite.objects.filter(user=self.user))

        self.assertTrue(csv_text.startswith("\ufeff"))
        self.assertIn("'=ligar", csv_text)
        self.assertNotIn("+245000", csv_text)
        self.assertNotIn("+245111", csv_text)
        self.assertNotIn("Rua privada", csv_text)
        self.assertNotIn("Guiné-Bissau", csv_text)

    def test_build_shortlist_csv_hides_current_values_missing_from_published_snapshot(self):
        self.profile.professional_title = "Titulo actual secreto"
        self.profile.location = "Cidade actual secreta"
        self.profile.country = "Pais actual secreto"
        self.profile.work_preference = Profile.WorkPreference.ONSITE
        self.profile.availability = Profile.Availability.UNAVAILABLE
        self.profile.published_snapshot = {"public_name": "Nome aprovado"}
        self.profile.save()

        csv_text = build_shortlist_csv(self.user, Favorite.objects.filter(user=self.user))

        self.assertIn("Nome aprovado", csv_text)
        self.assertNotIn("Titulo actual secreto", csv_text)
        self.assertNotIn("Cidade actual secreta", csv_text)
        self.assertNotIn("Pais actual secreto", csv_text)
        self.assertNotIn("Presencial", csv_text)
        self.assertNotIn("Indisponível", csv_text)

    def test_build_shortlist_csv_excludes_another_users_favorite_metadata(self):
        private_tag = RecruitmentTag.objects.create(user=self.other_user, name="Confidencial")
        other_favorite = Favorite.objects.create(
            user=self.other_user,
            profile=self.profile,
            notes="Notas privadas de outro utilizador",
        )
        other_favorite.tags.add(private_tag)

        csv_text = build_shortlist_csv(
            self.user,
            Favorite.objects.filter(pk__in=[self.favorite.pk, other_favorite.pk]),
        )

        self.assertNotIn("Notas privadas de outro utilizador", csv_text)
        self.assertNotIn("Confidencial", csv_text)

    def test_build_shortlist_csv_excludes_cross_user_tag_on_owned_favorite(self):
        private_tag = RecruitmentTag.objects.create(user=self.other_user, name="Etiqueta privada")
        self.favorite.tags.add(private_tag)

        csv_text = build_shortlist_csv(self.user, Favorite.objects.filter(user=self.user))

        self.assertNotIn("Etiqueta privada", csv_text)

    def test_build_shortlist_csv_prefetches_owned_tags_for_multiple_favorites(self):
        self.profile.published_snapshot = {"public_name": self.profile.public_name}
        self.profile.save(update_fields=("published_snapshot", "updated_at"))
        owner = get_user_model().objects.create_user(email="segundo-profissional@example.com", password="test-pass")
        second_profile = owner.profile
        second_profile.status = Profile.Status.APPROVED
        second_profile.is_public = True
        second_profile.published_snapshot = {"public_name": "Segundo profissional"}
        second_profile.save()
        second_favorite = Favorite.objects.create(user=self.user, profile=second_profile)
        self.favorite.tags.add(RecruitmentTag.objects.create(user=self.user, name="Primeira"))
        second_favorite.tags.add(RecruitmentTag.objects.create(user=self.user, name="Segunda"))

        with self.assertNumQueries(2):
            build_shortlist_csv(self.user, Favorite.objects.filter(user=self.user))

    def test_get_comparable_favorites_limits_and_orders_unique_numeric_ids(self):
        profiles = []
        for index in range(5):
            owner = get_user_model().objects.create_user(
                email=f"profissional-{index}@example.com", password="test-pass"
            )
            profile = owner.profile
            profile.status = Profile.Status.APPROVED
            profile.is_public = True
            profile.save()
            Favorite.objects.create(user=self.user, profile=profile)
            profiles.append(profile)

        requested_ids = [profiles[2].pk, "invalid", profiles[0].pk, profiles[2].pk, profiles[4].pk, profiles[1].pk]

        favorites = list(get_comparable_favorites(self.user, requested_ids))

        self.assertEqual([favorite.profile_id for favorite in favorites], [profiles[2].pk, profiles[0].pk, profiles[4].pk, profiles[1].pk])
