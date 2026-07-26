from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from interactions.models import Favorite, Notification, ProfileLike, RecruitmentTag, Report, SavedSearch
from profiles.models import Profile


class InteractionModelTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(email="user@example.com", password="test-pass")
        owner = user_model.objects.create_user(email="owner@example.com", password="test-pass")
        self.profile = owner.profile
        self.profile.status = Profile.Status.APPROVED
        self.profile.is_public = True
        self.profile.save()

    def test_favorite_and_like_are_unique_per_user_and_profile(self):
        Favorite.objects.create(user=self.user, profile=self.profile)
        ProfileLike.objects.create(user=self.user, profile=self.profile)

        with self.assertRaises(IntegrityError), transaction.atomic():
            Favorite.objects.create(user=self.user, profile=self.profile)
        with self.assertRaises(IntegrityError), transaction.atomic():
            ProfileLike.objects.create(user=self.user, profile=self.profile)

    def test_only_one_active_report_is_allowed(self):
        Report.objects.create(reporter=self.user, profile=self.profile, reason=Report.Reason.FRAUD)

        with self.assertRaises(IntegrityError), transaction.atomic():
            Report.objects.create(reporter=self.user, profile=self.profile, reason=Report.Reason.FALSE_DATA)

    def test_notification_starts_unread(self):
        notification = Notification.objects.create(user=self.user, type="test", title="Teste")
        self.assertIsNone(notification.read_at)

    def test_recruitment_tag_normalises_name_when_created(self):
        tag = RecruitmentTag.objects.create(user=self.user, name="  Engenharia Civil  ")

        self.assertEqual(tag.name, "Engenharia Civil")
        self.assertEqual(tag.normalized_name, "engenharia civil")

    def test_recruitment_tag_manager_normalises_whitespace_and_case(self):
        name = RecruitmentTag.objects.normalise_name("  ENGENHARIA   Civil  ")

        self.assertEqual(name, "engenharia civil")

    def test_recruitment_tag_rejects_name_that_exceeds_limit_after_casefold(self):
        with self.assertRaises(ValidationError):
            RecruitmentTag.objects.create(user=self.user, name="ß" * 80)

        self.assertFalse(RecruitmentTag.objects.filter(user=self.user).exists())

    def test_favorite_can_store_recruitment_status_notes_and_tags(self):
        tag = RecruitmentTag.objects.create(user=self.user, name="Engenharia Civil")
        favorite = Favorite.objects.create(
            user=self.user,
            profile=self.profile,
            status=Favorite.Status.TO_CONTACT,
            notes="Boa opção",
        )
        favorite.tags.add(tag)

        self.assertEqual(favorite.status, Favorite.Status.TO_CONTACT)
        self.assertEqual(favorite.notes, "Boa opção")
        self.assertEqual(favorite.tags.first(), tag)

    def test_saved_search_removes_unknown_and_blank_query_parameters(self):
        saved = SavedSearch.objects.create(
            user=self.user,
            name="Engenheiros",
            query_params={"q": "engenheiro", "experience": "5", "unsafe": "x", "sector": ""},
        )
        saved.full_clean()

        self.assertEqual(saved.query_params, {"q": "engenheiro", "experience": "5"})

    def test_saved_search_exposes_only_allowed_query_parameters(self):
        self.assertEqual(
            SavedSearch.allowed_query_params(),
            {
                "q",
                "sector",
                "area",
                "specialization",
                "skill",
                "location",
                "country",
                "availability",
                "work_preference",
                "seniority",
                "language",
                "experience",
                "cv",
                "order",
            },
        )

    def test_saved_search_rejects_non_object_query_parameters(self):
        saved = SavedSearch(user=self.user, name="Pesquisa inválida", query_params=["q"])

        with self.assertRaises(ValidationError):
            saved.full_clean()
