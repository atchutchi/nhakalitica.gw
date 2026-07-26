from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from memberships.models import Membership, MembershipDecision
from memberships.services import transition_membership


class MembershipTransitionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="candidate@example.com",
            password="safe-password-123",
        )
        self.reviewer = get_user_model().objects.create_user(
            email="reviewer@example.com",
            password="safe-password-123",
            is_staff=True,
        )
        self.membership = self.user.membership
        self.membership.member_type = Membership.Type.EFFECTIVE
        self.membership.relationship = Membership.Relationship.DIASPORA
        self.membership.relationship_note = "Membro da diáspora guineense."
        self.membership.status = Membership.Status.UNDER_REVIEW
        self.membership.save()

    def test_refusal_requires_note(self):
        with self.assertRaisesMessage(ValidationError, "justificação"):
            transition_membership(
                self.membership,
                self.reviewer,
                Membership.Status.REFUSED,
                "",
            )

    def test_corrections_require_note(self):
        with self.assertRaisesMessage(ValidationError, "justificação"):
            transition_membership(
                self.membership,
                self.reviewer,
                Membership.Status.CORRECTIONS_REQUIRED,
                "   ",
            )

    def test_approval_records_actor_and_decision_time(self):
        decision = transition_membership(
            self.membership,
            self.reviewer,
            Membership.Status.APPROVED,
            "Ligação confirmada.",
        )

        self.membership.refresh_from_db()
        self.assertEqual(self.membership.status, Membership.Status.APPROVED)
        self.assertIsNotNone(self.membership.decided_at)
        self.assertEqual(decision.actor, self.reviewer)
        self.assertEqual(decision.from_status, Membership.Status.UNDER_REVIEW)
        self.assertEqual(decision.to_status, Membership.Status.APPROVED)
        self.assertEqual(MembershipDecision.objects.count(), 1)

    def test_invalid_transition_is_rejected_without_partial_decision(self):
        self.membership.status = Membership.Status.DRAFT
        self.membership.save(update_fields=["status"])

        with self.assertRaisesMessage(ValidationError, "transição"):
            transition_membership(
                self.membership,
                self.reviewer,
                Membership.Status.APPROVED,
                "Aprovação directa.",
            )

        self.membership.refresh_from_db()
        self.assertEqual(self.membership.status, Membership.Status.DRAFT)
        self.assertFalse(MembershipDecision.objects.exists())
