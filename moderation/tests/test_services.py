from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from moderation.models import AuditLog
from moderation.services import moderate_profile
from profiles.models import Profile


class ModerationServiceTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.moderator = user_model.objects.create_user(
            email="moderador@cvlink.gw", password="test-pass", is_staff=True
        )
        self.professional = user_model.objects.create_user(
            email="profissional@cvlink.gw", password="test-pass"
        )
        self.profile = self.professional.profile
        self.profile.status = Profile.Status.PENDING
        self.profile.save()

    def test_approval_publishes_profile_and_records_decision(self):
        moderate_profile(self.profile, self.moderator, "approve")

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.status, Profile.Status.APPROVED)
        self.assertTrue(self.profile.is_public)
        self.assertEqual(self.profile.reviewed_by, self.moderator)
        self.assertIsNotNone(self.profile.reviewed_at)
        self.assertEqual(self.profile.published_snapshot["public_name"], self.profile.public_name)
        self.assertEqual(AuditLog.objects.get().action, "profile.approved")

    def test_rejected_changes_keep_previous_public_version(self):
        self.profile.public_name = "Versão aprovada"
        self.profile.professional_title = "Título aprovado"
        self.profile.status = Profile.Status.APPROVED
        self.profile.is_public = True
        self.profile.published_snapshot = self.profile.build_public_snapshot()
        self.profile.status = Profile.Status.CHANGES_PENDING
        self.profile.professional_title = "Título não aprovado"
        self.profile.save()

        moderate_profile(self.profile, self.moderator, "reject", "Alteração inadequada")

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.status, Profile.Status.APPROVED)
        self.assertTrue(self.profile.is_public)
        self.assertEqual(self.profile.public_payload["professional_title"], "Título aprovado")

    def test_rejection_requires_reason(self):
        with self.assertRaises(ValidationError):
            moderate_profile(self.profile, self.moderator, "reject", "")

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.status, Profile.Status.PENDING)
        self.assertFalse(AuditLog.objects.exists())

    def test_rejection_hides_profile_and_preserves_reason(self):
        moderate_profile(self.profile, self.moderator, "reject", "Currículo ilegível")

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.status, Profile.Status.REJECTED)
        self.assertFalse(self.profile.is_public)
        self.assertEqual(self.profile.review_note, "Currículo ilegível")

    def test_suspension_and_restoration_control_account_access(self):
        moderate_profile(self.profile, self.moderator, "suspend", "Conteúdo proibido")
        self.professional.refresh_from_db()
        self.assertFalse(self.professional.is_active)

        moderate_profile(self.profile, self.moderator, "restore", "Situação regularizada")
        self.professional.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertTrue(self.professional.is_active)
        self.assertEqual(self.profile.status, Profile.Status.DRAFT)
        self.assertFalse(self.profile.is_public)

    def test_audit_log_cannot_be_changed_or_deleted(self):
        moderate_profile(self.profile, self.moderator, "approve")
        event = AuditLog.objects.get()
        event.action = "profile.rejected"

        with self.assertRaises(ValidationError):
            event.save()
        with self.assertRaises(ValidationError):
            event.delete()
