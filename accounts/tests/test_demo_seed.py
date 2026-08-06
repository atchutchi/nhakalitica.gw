import os
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from memberships.models import Membership
from profiles.models import Profile


DEMO_PASSWORDS = {
    "DEMO_SEED_ENABLED": "True",
    "DEMO_ADMIN_1_PASSWORD": "Admin-Um-Segura-2026!",
    "DEMO_ADMIN_2_PASSWORD": "Admin-Dois-Segura-2026!",
    "DEMO_MEMBER_1_PASSWORD": "Membro-Um-Segura-2026!",
    "DEMO_MEMBER_2_PASSWORD": "Membro-Dois-Segura-2026!",
}


class DemoAccountSeedTests(TestCase):
    @patch.dict(os.environ, DEMO_PASSWORDS, clear=False)
    def test_command_creates_two_admins_and_two_approved_members(self):
        output = StringIO()

        call_command("seed_demo_accounts", stdout=output)

        users = get_user_model().objects.filter(email__endswith="@demo.nhakalitica.gw")
        self.assertEqual(users.count(), 4)
        self.assertEqual(users.filter(is_staff=True, is_superuser=True).count(), 2)
        self.assertEqual(users.filter(is_staff=False, is_superuser=False).count(), 2)
        self.assertEqual(users.filter(email_verified_at__isnull=False).count(), 4)
        self.assertEqual(
            Membership.objects.filter(
                user__in=users,
                status=Membership.Status.APPROVED,
            ).count(),
            4,
        )
        self.assertEqual(
            Profile.objects.filter(
                user__in=users,
                status=Profile.Status.APPROVED,
                review_status=Profile.ReviewStatus.APPROVED,
                is_discoverable=True,
            ).count(),
            4,
        )
        self.assertTrue(
            get_user_model()
            .objects.get(email="admin.rede@demo.nhakalitica.gw")
            .check_password(DEMO_PASSWORDS["DEMO_ADMIN_1_PASSWORD"])
        )
        self.assertTrue(
            get_user_model()
            .objects.get(email="membro.bissau@demo.nhakalitica.gw")
            .check_password(DEMO_PASSWORDS["DEMO_MEMBER_1_PASSWORD"])
        )
        for password in DEMO_PASSWORDS.values():
            self.assertNotIn(password, output.getvalue())

    @patch.dict(os.environ, DEMO_PASSWORDS, clear=False)
    def test_command_is_idempotent(self):
        call_command("seed_demo_accounts")
        first_ids = set(
            get_user_model()
            .objects.filter(email__endswith="@demo.nhakalitica.gw")
            .values_list("id", flat=True)
        )

        call_command("seed_demo_accounts")

        second_ids = set(
            get_user_model()
            .objects.filter(email__endswith="@demo.nhakalitica.gw")
            .values_list("id", flat=True)
        )
        self.assertEqual(second_ids, first_ids)
        self.assertEqual(len(second_ids), 4)

    @patch.dict(os.environ, DEMO_PASSWORDS, clear=False)
    def test_command_preserves_an_existing_demo_password(self):
        call_command("seed_demo_accounts")
        admin = get_user_model().objects.get(email="admin.rede@demo.nhakalitica.gw")
        admin.set_password("Credencial-entregue-ao-administrador-2026!")
        admin.save(update_fields=("password",))

        call_command("seed_demo_accounts")

        admin.refresh_from_db()
        self.assertTrue(admin.check_password("Credencial-entregue-ao-administrador-2026!"))

    @patch.dict(os.environ, {"DEMO_SEED_ENABLED": "False"}, clear=False)
    def test_command_does_nothing_when_demo_seed_is_disabled(self):
        call_command("seed_demo_accounts")

        self.assertFalse(
            get_user_model().objects.filter(email__endswith="@demo.nhakalitica.gw").exists()
        )
