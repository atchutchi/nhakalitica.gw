from datetime import timedelta
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.services import restore_scheduled_account, schedule_account_deletion
from moderation.models import AuditLog
from profiles.models import Profile


class AccountDeletionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="deletion@example.com",
            password="PalavraPasseSegura2026!",
        )
        self.user.profile.status = Profile.Status.APPROVED
        self.user.profile.review_status = Profile.ReviewStatus.APPROVED
        self.user.profile.is_public = True
        self.user.profile.is_discoverable = True
        self.user.profile.save()

    def test_deactivation_schedules_deletion_in_thirty_days(self):
        now = timezone.now()

        schedule_account_deletion(self.user, now=now)

        self.user.refresh_from_db()
        self.user.profile.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.assertEqual(self.user.deletion_requested_at, now)
        self.assertEqual(self.user.scheduled_deletion_at, now + timedelta(days=30))
        self.assertEqual(self.user.profile.status, Profile.Status.ARCHIVED)
        self.assertEqual(self.user.profile.review_status, Profile.ReviewStatus.DRAFT)
        self.assertFalse(self.user.profile.is_public)
        self.assertFalse(self.user.profile.is_discoverable)

    def test_restore_before_deadline_reactivates_private_draft(self):
        now = timezone.now()
        schedule_account_deletion(self.user, now=now)

        restore_scheduled_account(self.user, now=now + timedelta(days=10))

        self.user.refresh_from_db()
        self.user.profile.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertIsNone(self.user.deletion_requested_at)
        self.assertIsNone(self.user.scheduled_deletion_at)
        self.assertEqual(self.user.profile.status, Profile.Status.DRAFT)
        self.assertFalse(self.user.profile.is_discoverable)

    def test_restore_after_deadline_is_rejected(self):
        now = timezone.now()
        schedule_account_deletion(self.user, now=now)

        with self.assertRaises(ValidationError):
            restore_scheduled_account(self.user, now=now + timedelta(days=31))

    def test_dry_run_does_not_delete_expired_account(self):
        schedule_account_deletion(self.user, now=timezone.now() - timedelta(days=31))
        output = StringIO()

        call_command("purge_scheduled_accounts", "--dry-run", stdout=output)

        self.assertTrue(get_user_model().objects.filter(pk=self.user.pk).exists())
        self.assertIn(f"ID {self.user.pk}", output.getvalue())
        self.assertNotIn(self.user.email, output.getvalue())

    def test_command_deletes_only_expired_accounts(self):
        expired_user = self.user
        future_user = get_user_model().objects.create_user(
            email="future@example.com",
            password="PalavraPasseSegura2026!",
        )
        now = timezone.now()
        schedule_account_deletion(expired_user, now=now - timedelta(days=31))
        schedule_account_deletion(future_user, now=now)

        call_command("purge_scheduled_accounts", stdout=StringIO())

        self.assertFalse(get_user_model().objects.filter(pk=expired_user.pk).exists())
        self.assertTrue(get_user_model().objects.filter(pk=future_user.pk).exists())

    def test_purge_preserves_required_administrative_audit_record(self):
        user_id = self.user.pk
        AuditLog.objects.create(
            actor=self.user,
            action="account.deletion_scheduled",
            target_type="user",
            target_id=str(user_id),
            metadata={},
        )
        schedule_account_deletion(self.user, now=timezone.now() - timedelta(days=31))

        call_command("purge_scheduled_accounts", stdout=StringIO())

        event = AuditLog.objects.get(
            action="account.deletion_scheduled",
            target_id=str(user_id),
        )
        self.assertIsNone(event.actor)

    def test_admin_can_restore_account_within_recovery_period(self):
        administrator = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="PalavraPasseSegura2026!",
        )
        schedule_account_deletion(self.user, now=timezone.now())
        self.client.force_login(administrator)

        response = self.client.post(
            reverse("admin:accounts_user_changelist"),
            {
                "action": "restore_accounts_within_recovery_period",
                "_selected_action": [self.user.pk],
                "index": "0",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertIsNone(self.user.scheduled_deletion_at)
        self.assertTrue(
            AuditLog.objects.filter(
                actor=administrator,
                action="account.deletion_restored",
                target_id=str(self.user.pk),
            ).exists()
        )
