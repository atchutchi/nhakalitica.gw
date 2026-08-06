from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

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
