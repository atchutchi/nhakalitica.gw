from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from moderation.models import AuditLog
from profiles.models import Profile


class ModerationViewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.staff = user_model.objects.create_user(
            email="staff@cvlink.gw", password="test-pass", is_staff=True
        )
        self.superuser = user_model.objects.create_superuser(
            email="admin@cvlink.gw", password="test-pass"
        )
        self.member = user_model.objects.create_user(
            email="membro@cvlink.gw", password="test-pass"
        )
        self.profile = self.member.profile
        self.profile.public_name = "Pessoa Pendente"
        self.profile.status = Profile.Status.PENDING
        self.profile.save()

    def test_dashboard_requires_staff_access(self):
        response = self.client.get(reverse("moderation:dashboard"))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.member)
        response = self.client.get(reverse("moderation:dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_staff_sees_pending_profile_in_queue(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("moderation:profile-list"), {"status": "pending"})

        self.assertContains(response, "Pessoa Pendente")

    def test_staff_dashboard_uses_kalitica_admin_shell(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse("moderation:dashboard"))

        self.assertContains(response, 'class="admin-shell')
        self.assertContains(response, "Administração Kalitica")
        self.assertContains(response, "Candidaturas pendentes")
        self.assertContains(response, "css/admin.css?v=20260806-1")

    def test_admin_shell_offers_network_return_post_logout_and_current_section(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse("moderation:profile-list"))

        self.assertContains(response, "Voltar à rede")
        self.assertContains(response, 'method="post" action="/conta/sair/"')
        self.assertContains(response, 'aria-current="page"')
        self.assertEqual(response.content.decode().count('aria-current="page"'), 1)

    def test_admin_list_filters_have_accessible_labels(self):
        self.client.force_login(self.staff)

        for route_name, label in (
            ("moderation:membership-list", "Filtrar candidaturas por estado"),
            ("moderation:profile-list", "Filtrar perfis por estado"),
            ("moderation:report-list", "Filtrar denúncias por estado"),
        ):
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name))
                self.assertContains(response, label)

    def test_staff_can_approve_profile_using_post(self):
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse("moderation:profile-review", args=(self.profile.pk,)),
            {"action": "approve"},
        )

        self.assertRedirects(response, reverse("moderation:profile-list"))
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.status, Profile.Status.APPROVED)
        self.assertTrue(AuditLog.objects.filter(action="profile.approved").exists())

    def test_approved_profile_does_not_offer_approval_again(self):
        self.profile.status = Profile.Status.APPROVED
        self.profile.save(update_fields=("status",))
        self.client.force_login(self.staff)

        response = self.client.get(
            reverse("moderation:profile-review", args=(self.profile.pk,))
        )

        self.assertNotContains(response, "Aprovar publicação")
        self.assertContains(response, "Suspender")

    def test_rejection_without_reason_shows_validation_error(self):
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse("moderation:profile-review", args=(self.profile.pk,)),
            {"action": "reject", "reason": ""},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Indica o motivo")
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.status, Profile.Status.PENDING)

    def test_only_superuser_can_read_audit_log(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(reverse("moderation:audit-list")).status_code, 403)

        self.client.force_login(self.superuser)
        self.assertEqual(self.client.get(reverse("moderation:audit-list")).status_code, 200)

    def test_audit_search_is_labelled_and_table_cells_support_mobile_cards(self):
        AuditLog.objects.create(
            actor=self.superuser,
            action="profile.approved",
            target_type="profile",
            target_id=str(self.profile.pk),
            metadata={},
        )
        self.client.force_login(self.superuser)

        response = self.client.get(reverse("moderation:audit-list"))

        self.assertContains(response, "Pesquisar no histórico de auditoria")
        self.assertContains(response, 'data-label="Data"')
        self.assertContains(response, 'data-label="Acção"')

    def test_admin_filter_form_can_shrink_inside_a_mobile_workspace(self):
        admin_css = (Path(settings.BASE_DIR) / "static" / "css" / "admin.css").read_text(
            encoding="utf-8"
        )

        self.assertIn(".admin-page-heading form { grid-template-columns: minmax(0, 1fr) auto; }", admin_css)
        self.assertIn(".admin-page-heading input { min-width: 0; width: 100%; }", admin_css)

    def test_member_list_requires_staff_access(self):
        self.assertEqual(self.client.get(reverse("moderation:member-list")).status_code, 302)

        self.client.force_login(self.member)
        self.assertEqual(self.client.get(reverse("moderation:member-list")).status_code, 403)

    def test_member_list_searches_and_filters_accounts(self):
        self.member.first_name = "Binta"
        self.member.last_name = "Sambu"
        self.member.save()
        self.member.membership.member_type = "observer"
        self.member.membership.status = "approved"
        self.member.membership.save()
        self.client.force_login(self.staff)

        response = self.client.get(
            reverse("moderation:member-list"),
            {"q": "Binta", "account_state": "active", "member_type": "observer", "membership_status": "approved"},
        )

        self.assertContains(response, "Binta Sambu")
        self.assertContains(response, self.member.email)
        self.assertNotContains(response, self.superuser.email)

    def test_member_detail_shows_account_membership_and_profile_state(self):
        self.member.email_verified_at = timezone.now()
        self.member.save(update_fields=("email_verified_at",))
        self.client.force_login(self.staff)

        response = self.client.get(
            reverse("moderation:member-detail", args=(self.member.pk,))
        )

        self.assertContains(response, "Email confirmado")
        self.assertContains(response, "Adesão")
        self.assertContains(response, "Perfil profissional")
        self.assertContains(response, reverse("moderation:membership-review", args=(self.member.membership.pk,)))
        self.assertContains(response, reverse("moderation:profile-review", args=(self.member.profile.pk,)))
