from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from memberships.models import Membership
from profiles.models import Profile
from profiles.selectors import member_profiles


class MembershipProfileVisibilityTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(
            email="owner@example.com",
            password="Segura2026!",
        )
        self.viewer = get_user_model().objects.create_user(
            email="viewer@example.com",
            password="Segura2026!",
        )
        for user in (self.owner, self.viewer):
            user.membership.status = Membership.Status.APPROVED
            user.membership.save(update_fields=("status",))

        self.profile = self.owner.profile
        self.profile.public_name = "Membro Visível"
        self.profile.review_status = Profile.ReviewStatus.APPROVED
        self.profile.is_discoverable = True
        self.profile.save()

    def test_approved_membership_does_not_publish_draft_profile(self):
        self.profile.review_status = Profile.ReviewStatus.DRAFT
        self.profile.save(update_fields=("review_status",))

        self.assertFalse(self.profile.is_visible_to(self.viewer))

    def test_member_can_hide_approved_profile(self):
        self.profile.is_discoverable = False
        self.profile.save(update_fields=("is_discoverable",))

        self.assertFalse(self.profile.is_visible_to(self.viewer))

    def test_suspension_hides_profile_without_deleting_it(self):
        self.owner.membership.status = Membership.Status.SUSPENDED
        self.owner.membership.save(update_fields=("status",))

        self.assertFalse(self.profile.is_visible_to(self.viewer))
        self.assertTrue(Profile.objects.filter(pk=self.profile.pk).exists())

    def test_candidate_cannot_view_approved_profile(self):
        self.viewer.membership.status = Membership.Status.SUBMITTED
        self.viewer.membership.save(update_fields=("status",))

        self.assertFalse(self.profile.is_visible_to(self.viewer))

    def test_member_selector_excludes_suspended_profile_owner(self):
        self.owner.membership.status = Membership.Status.SUSPENDED
        self.owner.membership.save(update_fields=("status",))

        self.assertNotIn(self.profile, member_profiles(self.viewer))

    def test_approved_membership_does_not_publish_profile_automatically(self):
        new_member = get_user_model().objects.create_user(
            email="new-member@example.com",
            password="Segura2026!",
        )
        new_member.membership.status = Membership.Status.APPROVED
        new_member.membership.save(update_fields=("status",))

        self.assertFalse(new_member.profile.is_discoverable)
        self.assertEqual(
            new_member.profile.review_status,
            Profile.ReviewStatus.DRAFT,
        )

    def test_public_profile_uses_only_approved_organization_snapshot(self):
        self.owner.membership.represents_organization = True
        self.owner.membership.organization_name = "Organização Aprovada"
        self.owner.membership.organization_role = "Representante"
        self.owner.membership.organization_purpose = "Finalidade privada"
        self.owner.membership.save()
        self.profile.show_organization_on_profile = True
        self.profile.published_snapshot = self.profile.build_public_snapshot()
        self.profile.save(update_fields=("show_organization_on_profile", "published_snapshot"))
        self.owner.membership.organization_name = "Organização Ainda Não Revista"
        self.owner.membership.save(update_fields=("organization_name",))
        self.client.force_login(self.viewer)

        response = self.client.get(reverse("public-profile", args=(self.profile.slug,)))

        self.assertContains(response, "Organização representada")
        self.assertContains(response, "Organização Aprovada")
        self.assertContains(response, "Representante")
        self.assertNotContains(response, "Organização Ainda Não Revista")
        self.assertNotContains(response, "Finalidade privada")
