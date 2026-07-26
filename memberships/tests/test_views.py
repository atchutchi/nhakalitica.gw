from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from memberships.models import Membership, MembershipDecision


class MembershipApplicationViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="candidate@example.com",
            password="Segura2026!",
            first_name="Maria",
            last_name="Sambu",
        )
        self.membership = self.user.membership
        self.client.force_login(self.user)

    def complete_application(self):
        self.membership.member_type = Membership.Type.EFFECTIVE
        self.membership.relationship = Membership.Relationship.CITIZEN
        self.membership.motivation = "Quero contribuir para a rede profissional guineense."
        self.membership.accepts_code_of_conduct = True
        self.membership.accepts_privacy = True
        self.membership.confirms_truth = True
        self.membership.save()
        profile = self.user.profile
        profile.public_name = "Maria Sambu"
        profile.professional_title = "Gestora de projectos"
        profile.bio = "Experiência profissional em iniciativas de desenvolvimento."
        profile.save()

    def test_new_user_receives_membership_automatically(self):
        user = get_user_model().objects.create_user(
            email="automatic@example.com",
            password="Segura2026!",
        )

        self.assertEqual(user.membership.status, Membership.Status.DRAFT)
        self.assertIsNotNone(user.profile)

    def test_candidate_dashboard_shows_real_progress_and_private_shell(self):
        response = self.client.get(reverse("memberships:dashboard"))

        self.assertContains(response, 'class="onboarding-shell"')
        self.assertContains(response, 'class="application-progress"')
        self.assertContains(response, "A minha candidatura")
        self.assertContains(response, "0 de 6 etapas concluídas")
        self.assertContains(response, "Revisão manual")
        self.assertNotContains(response, "Directório")

    def test_submitted_dashboard_shows_review_timeline(self):
        self.membership.status = Membership.Status.UNDER_REVIEW
        self.membership.submitted_at = timezone.now()
        self.membership.save(update_fields=("status", "submitted_at"))

        response = self.client.get(reverse("memberships:dashboard"))

        self.assertContains(response, "Em análise")
        self.assertContains(response, 'class="application-timeline"')
        self.assertContains(response, "exige uma revisão específica")
        self.assertNotContains(response, "Continuar candidatura")

    def test_approved_dashboard_explains_separate_profile_review(self):
        self.membership.status = Membership.Status.APPROVED
        self.membership.save(update_fields=("status",))

        response = self.client.get(reverse("memberships:dashboard"))

        self.assertContains(response, "Adesão aprovada")
        self.assertContains(
            response,
            "A aprovação da adesão e a publicação do perfil são processos independentes",
        )
        self.assertContains(response, "depois de uma revisão específica")
        self.assertContains(response, reverse("search"))

    def test_candidate_can_save_draft(self):
        response = self.client.post(
            reverse("memberships:edit"),
            {
                "member_type": Membership.Type.OBSERVER,
                "relationship": Membership.Relationship.DIASPORA,
                "relationship_note": "",
                "motivation": "Quero reforçar a ligação profissional com a Guiné-Bissau.",
                "accepts_code_of_conduct": True,
                "accepts_privacy": True,
                "confirms_truth": True,
            },
        )

        self.assertRedirects(response, reverse("memberships:dashboard"))
        self.membership.refresh_from_db()
        self.assertEqual(self.membership.member_type, Membership.Type.OBSERVER)
        self.assertEqual(self.membership.status, Membership.Status.DRAFT)

    def test_unverified_candidate_cannot_submit(self):
        self.complete_application()

        response = self.client.post(reverse("memberships:submit"))

        self.assertRedirects(response, reverse("memberships:review"))
        self.membership.refresh_from_db()
        self.assertEqual(self.membership.status, Membership.Status.DRAFT)

    def test_submission_requires_minimum_professional_profile(self):
        self.complete_application()
        self.user.email_verified_at = timezone.now()
        self.user.save(update_fields=("email_verified_at",))
        self.user.profile.bio = ""
        self.user.profile.save(update_fields=("bio",))

        response = self.client.post(reverse("memberships:submit"))

        self.assertRedirects(response, reverse("memberships:review"))
        self.membership.refresh_from_db()
        self.assertEqual(self.membership.status, Membership.Status.DRAFT)

    def test_submission_locks_application_until_corrections(self):
        self.complete_application()
        self.user.email_verified_at = timezone.now()
        self.user.save(update_fields=("email_verified_at",))

        response = self.client.post(reverse("memberships:submit"))

        self.assertRedirects(response, reverse("memberships:dashboard"))
        self.membership.refresh_from_db()
        self.assertEqual(self.membership.status, Membership.Status.SUBMITTED)
        self.assertIsNotNone(self.membership.submitted_at)
        self.assertTrue(
            MembershipDecision.objects.filter(
                membership=self.membership,
                from_status=Membership.Status.DRAFT,
                to_status=Membership.Status.SUBMITTED,
            ).exists()
        )
        self.assertRedirects(
            self.client.get(reverse("memberships:edit")),
            reverse("memberships:dashboard"),
        )

    def test_corrections_required_reopens_application(self):
        self.membership.status = Membership.Status.CORRECTIONS_REQUIRED
        self.membership.save(update_fields=("status",))

        response = self.client.get(reverse("memberships:edit"))

        self.assertEqual(response.status_code, 200)
