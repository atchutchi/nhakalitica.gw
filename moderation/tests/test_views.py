from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from moderation.models import AuditLog
from profiles.models import Profile


class ModerationViewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.staff = user_model.objects.create_user(
            email="staff@cvlink.gw", password="test-pass", is_staff=True
        )
        self.superuser = user_model.objects.create_superuser(
            email="admin@cvlink.gw", password="test-pass"
        )
        self.member = user_model.objects.create_user(
            email="membro@cvlink.gw", password="test-pass"
        )
        self.profile = self.member.profile
        self.profile.public_name = "Pessoa Pendente"
        self.profile.status = Profile.Status.PENDING
        self.profile.save()

    def test_dashboard_requires_staff_access(self):
        response = self.client.get(reverse("moderation:dashboard"))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.member)
        response = self.client.get(reverse("moderation:dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_staff_sees_pending_profile_in_queue(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("moderation:profile-list"), {"status": "pending"})

        self.assertContains(response, "Pessoa Pendente")

    def test_staff_can_approve_profile_using_post(self):
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse("moderation:profile-review", args=(self.profile.pk,)),
            {"action": "approve"},
        )

        self.assertRedirects(response, reverse("moderation:profile-list"))
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.status, Profile.Status.APPROVED)
        self.assertTrue(AuditLog.objects.filter(action="profile.approved").exists())

    def test_rejection_without_reason_shows_validation_error(self):
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse("moderation:profile-review", args=(self.profile.pk,)),
            {"action": "reject", "reason": ""},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Indica o motivo")
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.status, Profile.Status.PENDING)

    def test_only_superuser_can_read_audit_log(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(reverse("moderation:audit-list")).status_code, 403)

        self.client.force_login(self.superuser)
        self.assertEqual(self.client.get(reverse("moderation:audit-list")).status_code, 200)
