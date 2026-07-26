from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from interactions.models import Notification
from memberships.models import Membership, MembershipDecision
from moderation.models import AuditLog
from profiles.models import Profile


class MembershipModerationTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.reviewer = user_model.objects.create_user(
            email="reviewer@example.com",
            password="Segura2026!",
            is_staff=True,
        )
        self.member = user_model.objects.create_user(
            email="member@example.com",
            password="Segura2026!",
        )
        self.applicant = user_model.objects.create_user(
            email="applicant@example.com",
            password="Segura2026!",
        )
        self.application = self.applicant.membership
        self.application.member_type = Membership.Type.EFFECTIVE
        self.application.relationship = Membership.Relationship.CITIZEN
        self.application.motivation = "Quero contribuir para a rede Kalitica."
        self.application.status = Membership.Status.SUBMITTED
        self.application.save()

    def test_non_staff_cannot_review_membership(self):
        self.client.force_login(self.member)

        response = self.client.get(
            reverse(
                "moderation:membership-review",
                args=(self.application.pk,),
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_approval_records_transition_audit_and_notification(self):
        self.client.force_login(self.reviewer)

        response = self.client.post(
            reverse(
                "moderation:membership-review",
                args=(self.application.pk,),
            ),
            {"action": Membership.Status.APPROVED, "note": "Ligação confirmada."},
        )

        self.assertRedirects(response, reverse("moderation:membership-list"))
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, Membership.Status.APPROVED)
        decision = MembershipDecision.objects.get(membership=self.application)
        self.assertEqual(decision.actor, self.reviewer)
        self.assertEqual(decision.to_status, Membership.Status.APPROVED)
        self.assertTrue(
            AuditLog.objects.filter(
                action="membership.approved",
                target_type="membership",
                target_id=str(self.application.pk),
            ).exists()
        )
        self.assertTrue(
            Notification.objects.filter(
                user=self.applicant,
                type="membership_approved",
            ).exists()
        )

    def test_corrections_require_a_reason(self):
        self.client.force_login(self.reviewer)

        response = self.client.post(
            reverse(
                "moderation:membership-review",
                args=(self.application.pk,),
            ),
            {"action": Membership.Status.CORRECTIONS_REQUIRED, "note": ""},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "justificação")
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, Membership.Status.SUBMITTED)
        self.assertFalse(MembershipDecision.objects.exists())

    def test_suspension_hides_profile_without_disabling_account(self):
        self.application.status = Membership.Status.APPROVED
        self.application.save(update_fields=("status",))
        profile = self.applicant.profile
        profile.review_status = Profile.ReviewStatus.APPROVED
        profile.is_discoverable = True
        profile.save(update_fields=("review_status", "is_discoverable"))
        self.client.force_login(self.reviewer)

        response = self.client.post(
            reverse(
                "moderation:membership-review",
                args=(self.application.pk,),
            ),
            {"action": Membership.Status.SUSPENDED, "note": "Incumprimento confirmado."},
        )

        self.assertRedirects(response, reverse("moderation:membership-list"))
        self.application.refresh_from_db()
        self.applicant.refresh_from_db()
        self.assertEqual(self.application.status, Membership.Status.SUSPENDED)
        self.assertTrue(self.applicant.is_active)
        self.assertTrue(Profile.objects.filter(pk=profile.pk).exists())

    def test_reactivation_restores_membership_access(self):
        self.application.status = Membership.Status.SUSPENDED
        self.application.save(update_fields=("status",))
        self.client.force_login(self.reviewer)

        response = self.client.post(
            reverse(
                "moderation:membership-review",
                args=(self.application.pk,),
            ),
            {"action": Membership.Status.APPROVED, "note": "Situação regularizada."},
        )

        self.assertRedirects(response, reverse("moderation:membership-list"))
        self.application.refresh_from_db()
        self.assertTrue(self.application.can_access_network)
