from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase


class UserConfigurationTests(SimpleTestCase):
    def test_project_uses_custom_user_model(self):
        self.assertEqual(settings.AUTH_USER_MODEL, "accounts.User")


class UserManagerTests(TestCase):
    def test_create_user_normalizes_email_and_hashes_password(self):
        user = get_user_model().objects.create_user(
            email="Pessoa@EXAMPLE.COM",
            password="uma-palavra-passe-segura",
        )

        self.assertEqual(user.email, "pessoa@example.com")
        self.assertTrue(user.check_password("uma-palavra-passe-segura"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_requires_email(self):
        with self.assertRaisesMessage(ValueError, "O email é obrigatório."):
            get_user_model().objects.create_user(email="", password="segura")

    def test_create_superuser_sets_required_permissions(self):
        user = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="uma-palavra-passe-segura",
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_create_superuser_rejects_invalid_staff_flag(self):
        with self.assertRaisesMessage(
            ValueError,
            "O superutilizador deve ter is_staff=True.",
        ):
            get_user_model().objects.create_superuser(
                email="admin@example.com",
                password="segura",
                is_staff=False,
            )
