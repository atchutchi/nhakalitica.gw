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

    def test_radio_cards_do_not_render_empty_placeholder_choices(self):
        form = MembershipApplicationForm(instance=self.membership)

        self.assertNotIn("", [value for value, _label in form.fields["member_type"].choices])
        self.assertNotIn("", [value for value, _label in form.fields["relationship"].choices])

    def test_organization_fields_are_required_for_representative(self):
        form = MembershipApplicationForm(
            data=self.application_data(
                represents_organization=True,
                organization_name="",
                organization_role="",
                organization_purpose="",
            ),
            instance=self.membership,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("organization_name", form.errors)
        self.assertIn("organization_role", form.errors)
        self.assertIn("organization_purpose", form.errors)

    def test_disabling_representation_clears_private_fields_and_publication_consent(self):
        self.membership.represents_organization = True
        self.membership.organization_name = "Organização Teste"
        self.membership.organization_role = "Representante"
        self.membership.organization_purpose = "Procurar talento"
        self.membership.save()
        self.user.profile.show_organization_on_profile = True
        self.user.profile.save(update_fields=("show_organization_on_profile",))
        form = MembershipApplicationForm(
            data=self.application_data(represents_organization=False),
            instance=self.membership,
        )

        self.assertTrue(form.is_valid(), form.errors)
        form.save()

        self.membership.refresh_from_db()
        self.user.profile.refresh_from_db()
        self.assertEqual(self.membership.organization_name, "")
        self.assertEqual(self.membership.organization_role, "")
        self.assertEqual(self.membership.organization_purpose, "")
        self.assertFalse(self.user.profile.show_organization_on_profile)
