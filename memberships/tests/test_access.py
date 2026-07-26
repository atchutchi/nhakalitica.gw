from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from memberships.models import Membership


class PrivateNetworkAccessTests(TestCase):
    def create_user(self, email, status):
        user = get_user_model().objects.create_user(
            email=email,
            password="Segura2026!",
        )
        membership = user.membership
        membership.member_type = Membership.Type.EFFECTIVE
        membership.relationship = Membership.Relationship.CITIZEN
        membership.status = status
        membership.save()
        return user

    def test_anonymous_visitor_is_sent_to_login(self):
        response = self.client.get(reverse("search"))

        self.assertRedirects(
            response,
            f'{reverse("accounts:login")}?next={reverse("search")}',
        )

    def test_candidate_is_sent_to_membership_dashboard(self):
        candidate = self.create_user(
            "candidate@example.com",
            Membership.Status.SUBMITTED,
        )
        self.client.force_login(candidate)

        response = self.client.get(reverse("search"))

        self.assertRedirects(response, "/adesao/")

    def test_suspended_member_is_sent_to_membership_dashboard(self):
        suspended = self.create_user(
            "suspended@example.com",
            Membership.Status.SUSPENDED,
        )
        self.client.force_login(suspended)

        response = self.client.get(reverse("area-list"))

        self.assertRedirects(response, "/adesao/")

    def test_approved_member_can_open_directory(self):
        member = self.create_user(
            "member@example.com",
            Membership.Status.APPROVED,
        )
        self.client.force_login(member)

        response = self.client.get(reverse("search"))

        self.assertEqual(response.status_code, 200)
