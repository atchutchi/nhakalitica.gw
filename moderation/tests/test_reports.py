from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from interactions.models import Notification, Report
from moderation.models import AuditLog
from profiles.models import Profile


class ReportModerationTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.staff = user_model.objects.create_user(
            email="staff@example.com", password="test-pass", is_staff=True
        )
        self.reporter = user_model.objects.create_user(email="reporter@example.com", password="test-pass")
        owner = user_model.objects.create_user(email="owner-report@example.com", password="test-pass")
        profile = owner.profile
        profile.status = Profile.Status.APPROVED
        profile.is_public = True
        profile.save()
        self.report = Report.objects.create(
            reporter=self.reporter, profile=profile, reason=Report.Reason.FRAUD
        )

    def test_staff_can_see_open_reports(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("moderation:report-list"))
        self.assertContains(response, self.report.get_reason_display())

    def test_resolving_report_requires_note_and_creates_audit(self):
        self.client.force_login(self.staff)
        url = reverse("moderation:report-review", args=(self.report.pk,))
        response = self.client.post(url, {"action": "resolve", "note": ""})
        self.assertContains(response, "Indica a resolução")

        response = self.client.post(url, {"action": "resolve", "note": "Perfil verificado e corrigido."})
        self.assertRedirects(response, reverse("moderation:report-list"))
        self.report.refresh_from_db()
        self.assertEqual(self.report.status, Report.Status.RESOLVED)
        self.assertTrue(AuditLog.objects.filter(action="report.resolved").exists())
        self.assertTrue(Notification.objects.filter(user=self.reporter, type="report_resolved").exists())
