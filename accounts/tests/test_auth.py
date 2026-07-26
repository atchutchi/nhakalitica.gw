from django.contrib.auth import get_user_model
from django.test import TestCase


class AuthenticationFlowTests(TestCase):
    def test_signup_page_is_available(self):
        response = self.client.get("/conta/criar/")

        self.assertEqual(response.status_code, 200)

    def test_signup_creates_authenticated_user(self):
        response = self.client.post(
            "/conta/criar/",
            {
                "email": "maria@example.com",
                "first_name": "Maria",
                "last_name": "Sambu",
                "password1": "PalavraPasseSegura2026!",
                "password2": "PalavraPasseSegura2026!",
            },
        )

        self.assertRedirects(response, "/conta/painel/")
        self.assertTrue(get_user_model().objects.filter(email="maria@example.com").exists())
        self.assertIn("_auth_user_id", self.client.session)

    def test_user_can_login_with_email(self):
        get_user_model().objects.create_user(
            email="joao@example.com",
            password="PalavraPasseSegura2026!",
        )

        response = self.client.post(
            "/conta/entrar/",
            {"username": "joao@example.com", "password": "PalavraPasseSegura2026!"},
        )

        self.assertRedirects(response, "/conta/painel/")

    def test_dashboard_requires_authentication(self):
        response = self.client.get("/conta/painel/")

        self.assertRedirects(response, "/conta/entrar/?next=/conta/painel/")

    def test_authenticated_user_can_open_dashboard(self):
        user = get_user_model().objects.create_user(
            email="carlos@example.com",
            password="PalavraPasseSegura2026!",
        )
        self.client.force_login(user)

        response = self.client.get("/conta/painel/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rascunho")
        self.assertContains(response, "Completa o teu perfil")

    def test_user_can_logout_with_post(self):
        user = get_user_model().objects.create_user(
            email="fatu@example.com",
            password="PalavraPasseSegura2026!",
        )
        self.client.force_login(user)

        response = self.client.post("/conta/sair/")

        self.assertRedirects(response, "/conta/entrar/")
        self.assertNotIn("_auth_user_id", self.client.session)
