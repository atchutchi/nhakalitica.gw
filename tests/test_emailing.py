from unittest.mock import PropertyMock, patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from memberships.models import Membership
from moderation.services import moderate_membership, moderate_profile
from profiles.models import Profile


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    KALITICA_ADMIN_EMAILS=["equipa@nhakalitica.gw"],
    PUBLIC_BASE_URL="https://nhakalitica.gw",
)
class OperationalEmailTests(TestCase):
    def setUp(self):
        self.staff = get_user_model().objects.create_user(
            email="moderador@nhakalitica.gw",
            password="PalavraPasseSegura2026!",
            is_staff=True,
        )
        self.user = get_user_model().objects.create_user(
            email="membro@example.com",
            password="PalavraPasseSegura2026!",
        )

    def complete_membership(self):
        self.user.email_verified_at = timezone.now()
        self.user.save(update_fields=("email_verified_at",))
        membership = self.user.membership
        membership.member_type = Membership.Type.EFFECTIVE
        membership.relationship = Membership.Relationship.CITIZEN
        membership.motivation = "Quero contribuir para a comunidade profissional."
        membership.accepts_code_of_conduct = True
        membership.accepts_privacy = True
        membership.confirms_truth = True
        membership.save()
        profile = self.user.profile
        profile.public_name = "Maria Sambu"
        profile.professional_title = "Gestora"
        profile.bio = "Experiência em gestão de projectos."
        profile.save()
        return membership

    def test_membership_submission_emails_the_team(self):
        self.complete_membership()
        self.client.force_login(self.user)

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(reverse("memberships:submit"))

        self.assertRedirects(response, reverse("memberships:dashboard"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["equipa@nhakalitica.gw"])
        self.assertIn("Nova candidatura", mail.outbox[0].subject)
        self.assertIn("membro@example.com", mail.outbox[0].body)

    def test_membership_decision_emails_the_member(self):
        membership = self.complete_membership()
        membership.status = Membership.Status.SUBMITTED
        membership.save(update_fields=("status",))

        with self.captureOnCommitCallbacks(execute=True):
            moderate_membership(
                membership,
                self.staff,
                Membership.Status.APPROVED,
                "Ligação confirmada.",
            )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user.email])
        self.assertIn("Adesão aprovada", mail.outbox[0].subject)
        self.assertIn("Ligação confirmada.", mail.outbox[0].body)

    def test_profile_submission_emails_the_team(self):
        self.user.email_verified_at = timezone.now()
        self.user.save(update_fields=("email_verified_at",))
        self.user.membership.status = Membership.Status.APPROVED
        self.user.membership.save(update_fields=("status",))
        self.client.force_login(self.user)

        with patch.object(Profile, "can_submit", new_callable=PropertyMock, return_value=True):
            with self.captureOnCommitCallbacks(execute=True):
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
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["equipa@nhakalitica.gw"])
        self.assertIn("Novo perfil", mail.outbox[0].subject)

    def test_profile_decision_emails_the_member(self):
        profile = self.user.profile
        profile.status = Profile.Status.PENDING
        profile.save(update_fields=("status",))

        with self.captureOnCommitCallbacks(execute=True):
            moderate_profile(profile, self.staff, "approve")

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user.email])
        self.assertIn("Perfil aprovado", mail.outbox[0].subject)

    @patch("core.emailing.send_mail", side_effect=RuntimeError("smtp unavailable"))
    def test_email_failure_does_not_rollback_approved_membership(self, mocked_send):
        membership = self.complete_membership()
        membership.status = Membership.Status.SUBMITTED
        membership.save(update_fields=("status",))

        with self.captureOnCommitCallbacks(execute=True):
            moderate_membership(
                membership,
                self.staff,
                Membership.Status.APPROVED,
            )

        membership.refresh_from_db()
        self.assertEqual(membership.status, Membership.Status.APPROVED)
        mocked_send.assert_called_once()
