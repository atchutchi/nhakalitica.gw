from unittest.mock import PropertyMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.legal import record_legal_acceptance
from accounts.models import LegalAcceptance
from memberships.models import Membership
from profiles.models import Profile


class LegalAcceptanceTests(TestCase):
    def valid_signup_data(self):
        return {
            "email": "legal@example.com",
            "first_name": "Maria",
            "last_name": "Sambu",
            "country": "Guiné-Bissau",
            "accept_terms": "on",
            "password1": "PalavraPasseSegura2026!",
            "password2": "PalavraPasseSegura2026!",
        }

    def test_signup_records_terms_and_privacy_once(self):
        response = self.client.post(reverse("accounts:signup"), self.valid_signup_data())

        user = get_user_model().objects.get(email="legal@example.com")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            LegalAcceptance.objects.filter(
                user=user,
                document_type=LegalAcceptance.DocumentType.TERMS,
                version="1.0",
                source=LegalAcceptance.Source.SIGNUP,
            ).exists()
        )
        self.assertTrue(
            LegalAcceptance.objects.filter(
                user=user,
                document_type=LegalAcceptance.DocumentType.PRIVACY,
                version="1.0",
                source=LegalAcceptance.Source.SIGNUP,
            ).exists()
        )

    def test_recording_same_acceptance_is_idempotent(self):
        user = get_user_model().objects.create_user(
            email="idempotent@example.com",
            password="PalavraPasseSegura2026!",
        )

        first = record_legal_acceptance(
            user,
            LegalAcceptance.DocumentType.PRIVACY,
            LegalAcceptance.Source.MEMBERSHIP,
        )
        second = record_legal_acceptance(
            user,
            LegalAcceptance.DocumentType.PRIVACY,
            LegalAcceptance.Source.MEMBERSHIP,
        )

        self.assertEqual(first.pk, second.pk)
        self.assertEqual(user.legal_acceptances.count(), 1)

    def test_invalid_signup_does_not_record_acceptance(self):
        data = self.valid_signup_data()
        data["accept_terms"] = ""

        response = self.client.post(reverse("accounts:signup"), data)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(LegalAcceptance.objects.exists())

    def test_membership_submission_records_privacy_and_code(self):
        user = get_user_model().objects.create_user(
            email="membership-legal@example.com",
            password="PalavraPasseSegura2026!",
        )
        user.email_verified_at = timezone.now()
        user.save(update_fields=("email_verified_at",))
        membership = user.membership
        membership.member_type = Membership.Type.EFFECTIVE
        membership.relationship = Membership.Relationship.CITIZEN
        membership.motivation = "Quero contribuir para a comunidade profissional."
        membership.accepts_code_of_conduct = True
        membership.accepts_privacy = True
        membership.confirms_truth = True
        membership.save()
        profile = user.profile
        profile.public_name = "Maria Sambu"
        profile.professional_title = "Gestora"
        profile.bio = "Experiência em gestão de projectos."
        profile.save()
        self.client.force_login(user)

        response = self.client.post(reverse("memberships:submit"))

        self.assertRedirects(response, reverse("memberships:dashboard"))
        self.assertTrue(
            user.legal_acceptances.filter(
                document_type=LegalAcceptance.DocumentType.PRIVACY,
                source=LegalAcceptance.Source.MEMBERSHIP,
                version="1.0",
            ).exists()
        )
        self.assertTrue(
            user.legal_acceptances.filter(
                document_type=LegalAcceptance.DocumentType.CODE,
                source=LegalAcceptance.Source.MEMBERSHIP,
                version="1.0",
            ).exists()
        )

    def test_invalid_membership_submission_does_not_record_acceptance(self):
        user = get_user_model().objects.create_user(
            email="invalid-membership@example.com",
            password="PalavraPasseSegura2026!",
        )
        user.email_verified_at = timezone.now()
        user.save(update_fields=("email_verified_at",))
        self.client.force_login(user)

        response = self.client.post(reverse("memberships:submit"))

        self.assertRedirects(response, reverse("memberships:review"))
        self.assertFalse(user.legal_acceptances.exists())

    def test_invalid_profile_submission_does_not_record_acceptance(self):
        user = get_user_model().objects.create_user(
            email="invalid-profile@example.com",
            password="PalavraPasseSegura2026!",
        )
        membership = user.membership
        membership.status = Membership.Status.APPROVED
        membership.save(update_fields=("status",))
        self.client.force_login(user)

        response = self.client.post(
            reverse("profiles:submit"),
            {
                "consent_profile_public": "on",
                "consent_contact": "on",
                "accept_terms": "on",
                "accept_privacy": "on",
            },
        )

        self.assertRedirects(response, reverse("accounts:dashboard"))
        self.assertFalse(user.legal_acceptances.exists())

    def test_profile_submission_records_terms_and_privacy_and_keeps_history(self):
        user = get_user_model().objects.create_user(
            email="profile-legal@example.com",
            password="PalavraPasseSegura2026!",
        )
        user.email_verified_at = timezone.now()
        user.save(update_fields=("email_verified_at",))
        membership = user.membership
        membership.status = Membership.Status.APPROVED
        membership.save(update_fields=("status",))
        self.client.force_login(user)

        with patch.object(Profile, "can_submit", new_callable=PropertyMock, return_value=True):
            response = self.client.post(
                reverse("profiles:submit"),
                {
                    "consent_profile_public": "on",
                    "consent_contact": "on",
                    "accept_terms": "on",
                    "accept_privacy": "on",
                },
            )

        self.assertRedirects(response, reverse("accounts:dashboard"))
        profile = user.profile
        profile.refresh_from_db()
        self.assertEqual(profile.accepted_terms_version, "1.0")
        self.assertEqual(profile.accepted_privacy_version, "1.0")
        self.assertIsNotNone(profile.accepted_terms_at)
        self.assertIsNotNone(profile.accepted_privacy_at)
        self.assertTrue(
            user.legal_acceptances.filter(
                document_type=LegalAcceptance.DocumentType.TERMS,
                source=LegalAcceptance.Source.PROFILE,
                version="1.0",
            ).exists()
        )
        self.assertTrue(
            user.legal_acceptances.filter(
                document_type=LegalAcceptance.DocumentType.PRIVACY,
                source=LegalAcceptance.Source.PROFILE,
                version="1.0",
            ).exists()
        )
