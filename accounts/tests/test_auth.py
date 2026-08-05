from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone


class AuthenticationFlowTests(TestCase):
    def test_signup_page_is_available(self):
        response = self.client.get("/conta/criar/")

        self.assertEqual(response.status_code, 200)

    @override_settings(PUBLIC_SIGNUP_ENABLED=False)
    def test_demo_environment_blocks_public_signup(self):
        response = self.client.post(
            "/conta/criar/",
            {
                "email": "novo-membro@example.com",
                "first_name": "Novo",
                "last_name": "Membro",
                "country": "Guiné-Bissau",
                "accept_terms": "on",
                "password1": "PalavraPasseSegura2026!",
                "password2": "PalavraPasseSegura2026!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ambiente de demonstração")
        self.assertFalse(
            get_user_model().objects.filter(email="novo-membro@example.com").exists()
        )

    def test_authentication_fields_expose_browser_autocomplete_hints(self):
        login_response = self.client.get("/conta/entrar/")
        signup_response = self.client.get("/conta/criar/")

        self.assertContains(login_response, 'autocomplete="email"')
        self.assertContains(login_response, 'autocomplete="current-password"')
        self.assertContains(signup_response, 'autocomplete="given-name"')
        self.assertContains(signup_response, 'autocomplete="family-name"')
        self.assertContains(signup_response, 'autocomplete="country-name"')

    def test_signup_waits_for_email_confirmation(self):
        response = self.client.post(
            "/conta/criar/",
            {
                "email": "maria@example.com",
                "first_name": "Maria",
                "last_name": "Sambu",
                "country": "Guiné-Bissau",
                "accept_terms": "on",
                "password1": "PalavraPasseSegura2026!",
                "password2": "PalavraPasseSegura2026!",
            },
        )

        self.assertRedirects(response, "/conta/confirmar-email/")
        self.assertTrue(get_user_model().objects.filter(email="maria@example.com").exists())
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_user_can_login_with_email(self):
        user = get_user_model().objects.create_user(
            email="joao@example.com",
            password="PalavraPasseSegura2026!",
        )
        user.email_verified_at = timezone.now()
        user.save(update_fields=("email_verified_at",))

        response = self.client.post(
            "/conta/entrar/",
            {"username": "joao@example.com", "password": "PalavraPasseSegura2026!"},
        )

        self.assertRedirects(response, "/conta/painel/")

    def test_unverified_user_cannot_login(self):
        get_user_model().objects.create_user(
            email="por-confirmar@example.com",
            password="PalavraPasseSegura2026!",
        )

        response = self.client.post(
            "/conta/entrar/",
            {
                "username": "por-confirmar@example.com",
                "password": "PalavraPasseSegura2026!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Confirma o teu email")
        self.assertNotIn("_auth_user_id", self.client.session)

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

    def test_authenticated_header_exposes_account_menu_and_logout(self):
        user = get_user_model().objects.create_user(
            email="menu@example.com",
            password="PalavraPasseSegura2026!",
        )
        self.client.force_login(user)

        response = self.client.get("/conta/painel/")

        self.assertContains(response, 'data-account-menu')
        self.assertContains(response, 'href="/perfil/pre-visualizar/"')
        self.assertContains(response, 'href="/conta/editar/"')
        self.assertContains(response, 'href="/conta/alterar-palavra-passe/"')
        self.assertContains(response, 'action="/conta/sair/"')
        self.assertContains(response, "O meu perfil")
        self.assertContains(response, "Editar conta")
        self.assertContains(response, "Alterar palavra-passe")
        self.assertContains(response, "Sair")

    def test_user_can_logout_with_post(self):
        user = get_user_model().objects.create_user(
            email="fatu@example.com",
            password="PalavraPasseSegura2026!",
        )
        self.client.force_login(user)

        response = self.client.post("/conta/sair/")

        self.assertRedirects(response, "/conta/entrar/")
        self.assertNotIn("_auth_user_id", self.client.session)
