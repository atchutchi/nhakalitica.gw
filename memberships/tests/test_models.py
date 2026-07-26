from django.contrib.auth import get_user_model
from django.test import TestCase

from memberships.models import Membership


class MembershipModelTests(TestCase):
    def create_membership(self, member_type, status):
        user = get_user_model().objects.create_user(
            email=f"{member_type}-{status}@example.com",
            password="safe-password-123",
        )
        membership = user.membership
        membership.member_type = member_type
        membership.relationship = Membership.Relationship.CITIZEN
        membership.relationship_note = "Cidadão da Guiné-Bissau."
        membership.status = status
        membership.save()
        return membership

    def test_approved_membership_opens_network_for_both_types(self):
        for member_type in [Membership.Type.EFFECTIVE, Membership.Type.OBSERVER]:
            with self.subTest(member_type=member_type):
                membership = self.create_membership(
                    member_type,
                    Membership.Status.APPROVED,
                )
                self.assertTrue(membership.can_access_network)

    def test_suspended_membership_never_opens_network(self):
        membership = self.create_membership(
            Membership.Type.EFFECTIVE,
            Membership.Status.SUSPENDED,
        )

        self.assertFalse(membership.can_access_network)

    def test_candidate_membership_never_opens_network(self):
        for status in [
            Membership.Status.DRAFT,
            Membership.Status.SUBMITTED,
            Membership.Status.UNDER_REVIEW,
            Membership.Status.CORRECTIONS_REQUIRED,
            Membership.Status.REFUSED,
        ]:
            with self.subTest(status=status):
                membership = self.create_membership(
                    Membership.Type.OBSERVER,
                    status,
                )
                self.assertFalse(membership.can_access_network)
