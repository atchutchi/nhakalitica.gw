from django.contrib.auth import get_user_model
from django.test import TestCase

from profiles.models import Profile


class ProfileViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="maria@example.com",
            password="PalavraPasseSegura2026!",
        )

    def test_edit_requires_authentication(self):
        response = self.client.get("/perfil/editar/")

        self.assertRedirects(response, "/conta/entrar/?next=/perfil/editar/")

    def test_user_can_update_own_profile(self):
        self.client.force_login(self.user)

        response = self.client.post(
            "/perfil/editar/",
            {
                "public_name": "Maria Sambu",
                "professional_title": "Programadora",
                "bio": "Experiência em desenvolvimento de serviços digitais.",
                "location": "Bissau",
                "country": "Guiné-Bissau",
                "availability": "open",
                "work_preference": "hybrid",
                "contact_visibility": "form",
            },
        )

        self.assertRedirects(response, "/conta/painel/")
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.professional_title, "Programadora")

    def test_editing_approved_profile_requires_new_review(self):
        profile = self.user.profile
        profile.public_name = "Maria Sambu"
        profile.professional_title = "Programadora"
        profile.bio = "Perfil aprovado antes da alteração."
        profile.location = "Bissau"
        profile.status = Profile.Status.APPROVED
        profile.is_public = True
        profile.save()
        self.client.force_login(self.user)

        self.client.post(
            "/perfil/editar/",
            {
                "public_name": "Maria Sambu",
                "professional_title": "Programadora sénior",
                "bio": "Experiência em desenvolvimento de serviços digitais.",
                "location": "Bissau",
                "country": "Guiné-Bissau",
                "availability": "open",
                "work_preference": "hybrid",
                "contact_visibility": "form",
            },
        )

        profile.refresh_from_db()
        self.assertEqual(profile.status, Profile.Status.CHANGES_PENDING)
        self.assertTrue(profile.is_public)
        self.assertEqual(profile.revisions.filter(status="pending").count(), 1)
        public_response = self.client.get(f"/profissionais/{profile.slug}/")
        self.assertContains(public_response, "Programadora")
        self.assertNotContains(public_response, "Programadora sénior")

    def test_incomplete_profile_cannot_be_submitted(self):
        self.client.force_login(self.user)

        response = self.client.post(
            "/perfil/submeter/",
            {
                "consent_profile_public": "on",
                "consent_contact": "on",
                "accept_terms": "on",
                "accept_privacy": "on",
            },
        )

        self.assertRedirects(response, "/conta/painel/")
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.status, "draft")

    def test_user_can_add_experience(self):
        self.client.force_login(self.user)

        response = self.client.post(
            "/perfil/secao/experiencia/adicionar/",
            {
                "title": "Programadora",
                "organization": "CVLink",
                "location": "Bissau",
                "description": "Desenvolvimento da plataforma.",
                "start_date": "2025-01-01",
                "is_current": "on",
            },
        )

        self.assertRedirects(response, "/conta/painel/")
        self.assertTrue(self.user.profile.experiences.filter(title="Programadora").exists())

    def test_user_can_edit_own_experience(self):
        experience = self.user.profile.experiences.create(
            title="Programadora",
            organization="CVLink",
            start_date="2025-01-01",
        )
        self.client.force_login(self.user)
        response = self.client.post(
            f"/perfil/secao/experiencia/{experience.pk}/editar/",
            {
                "title": "Programadora sénior",
                "organization": "CVLink",
                "start_date": "2025-01-01",
            },
        )
        self.assertRedirects(response, "/conta/painel/")
        experience.refresh_from_db()
        self.assertEqual(experience.title, "Programadora sénior")

    def test_draft_preview_is_private_and_not_indexed(self):
        self.user.profile.public_name = "Maria Sambu"
        self.user.profile.save()
        response = self.client.get("/perfil/pre-visualizar/")
        self.assertRedirects(response, "/conta/entrar/?next=/perfil/pre-visualizar/")

        self.client.force_login(self.user)
        response = self.client.get("/perfil/pre-visualizar/")
        self.assertContains(response, "Pré-visualização privada")
        self.assertContains(response, 'content="noindex,nofollow"')

    def test_user_cannot_delete_another_users_experience(self):
        other = get_user_model().objects.create_user(
            email="outra@example.com",
            password="PalavraPasseSegura2026!",
        )
        experience = other.profile.experiences.create(
            title="Gestora",
            organization="Outra organização",
            start_date="2025-01-01",
        )
        self.client.force_login(self.user)

        response = self.client.post(f"/perfil/secao/experiencia/{experience.pk}/eliminar/")

        self.assertEqual(response.status_code, 404)
