from django.contrib.auth import get_user_model
from django.test import TestCase

from memberships.forms import MembershipApplicationForm
from memberships.models import Membership


class MembershipApplicationFormTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="candidate@example.com",
            password="Segura2026!",
        )
        self.membership = self.user.membership

    def application_data(self, **overrides):
        data = {
            "member_type": Membership.Type.OBSERVER,
            "relationship": Membership.Relationship.RELEVANT_LINK,
            "relationship_note": "Colaboro há cinco anos com organizações guineenses.",
            "motivation": "Quero colaborar com a rede profissional da Kalitica.",
            "accepts_code_of_conduct": True,
            "accepts_privacy": True,
            "confirms_truth": True,
        }
        data.update(overrides)
        return data

    def test_relevant_link_requires_explanation(self):
        form = MembershipApplicationForm(
            data=self.application_data(relationship_note=""),
            instance=self.membership,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("relationship_note", form.errors)

    def test_citizen_does_not_require_relationship_explanation(self):
        form = MembershipApplicationForm(
            data=self.application_data(
                relationship=Membership.Relationship.CITIZEN,
                relationship_note="",
            ),
            instance=self.membership,
        )

        self.assertTrue(form.is_valid(), form.errors)

    def test_all_consents_are_required(self):
        form = MembershipApplicationForm(
            data=self.application_data(accepts_privacy=False),
            instance=self.membership,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("accepts_privacy", form.errors)
