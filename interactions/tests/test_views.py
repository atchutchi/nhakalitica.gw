from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from interactions.models import (
    ContactRequest,
    Favorite,
    Notification,
    ProfileLike,
    RecruitmentTag,
    Report,
    SavedSearch,
)
from profiles.models import Education, Experience, Profile, ProfileLanguage
from memberships.models import Membership
from taxonomy.models import Skill


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class InteractionViewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(email="user@example.com", password="test-pass")
        self.user.email_verified_at = timezone.now()
        self.user.save(update_fields=("email_verified_at",))
        self.owner = user_model.objects.create_user(email="owner@example.com", password="test-pass")
        self.other_user = user_model.objects.create_user(email="other@example.com", password="test-pass")
        for user in (self.user, self.owner, self.other_user):
            Membership.objects.create(
                user=user,
                member_type=Membership.Type.EFFECTIVE,
                relationship=Membership.Relationship.CITIZEN,
                status=Membership.Status.APPROVED,
            )
        self.profile = self.owner.profile
        self.profile.public_name = "Profissional Público"
        self.profile.status = Profile.Status.APPROVED
        self.profile.is_public = True
        self.profile.consent_contact = True
        self.profile.save()

    def test_favorite_toggle_adds_and_removes_profile(self):
        self.client.force_login(self.user)
        url = reverse("interactions:favorite-toggle", args=(self.profile.slug,))

        self.client.post(url)
        self.assertTrue(Favorite.objects.filter(user=self.user, profile=self.profile).exists())
        self.client.post(url)
        self.assertFalse(Favorite.objects.filter(user=self.user, profile=self.profile).exists())

    def test_like_toggle_updates_total(self):
        self.client.force_login(self.user)
        self.client.post(reverse("interactions:like-toggle", args=(self.profile.slug,)))
        self.assertEqual(ProfileLike.objects.filter(profile=self.profile).count(), 1)

    def test_owner_cannot_interact_with_own_profile(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse("interactions:favorite-toggle", args=(self.profile.slug,)))
        self.assertEqual(response.status_code, 403)

    def test_contact_creates_private_request_notification_and_email(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("interactions:contact", args=(self.profile.slug,)),
            {"subject": "Proposta de projecto", "message": "Gostaria de apresentar uma oportunidade profissional."},
        )

        self.assertRedirects(response, reverse("interactions:contacts"))
        self.assertTrue(ContactRequest.objects.filter(sender=self.user, profile=self.profile).exists())
        self.assertTrue(Notification.objects.filter(user=self.owner, type="new_contact").exists())
        self.assertEqual(len(mail.outbox), 1)

    def test_unverified_sender_cannot_contact(self):
        self.user.email_verified_at = None
        self.user.save(update_fields=("email_verified_at",))
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("interactions:contact", args=(self.profile.slug,)),
            {"subject": "Proposta", "message": "Mensagem profissional suficientemente clara."},
        )
        self.assertContains(response, "Confirma o teu email")
        self.assertFalse(ContactRequest.objects.exists())

    def test_contact_rate_limit_blocks_fourth_message_in_one_hour(self):
        self.client.force_login(self.user)
        url = reverse("interactions:contact", args=(self.profile.slug,))
        payload = {"subject": "Proposta", "message": "Mensagem profissional suficientemente clara."}
        for _index in range(3):
            self.client.post(url, payload)

        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "limite de mensagens")
        self.assertEqual(ContactRequest.objects.count(), 3)

    def test_hidden_contact_preference_blocks_message(self):
        self.profile.contact_visibility = Profile.ContactVisibility.HIDDEN
        self.profile.save()
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("interactions:contact", args=(self.profile.slug,)),
            {"subject": "Proposta", "message": "Mensagem profissional suficientemente clara."},
        )
        self.assertContains(response, "não está a aceitar contactos")
        self.assertFalse(ContactRequest.objects.exists())

    def test_recipient_can_report_abusive_contact(self):
        contact = ContactRequest.objects.create(
            sender=self.user,
            profile=self.profile,
            subject="Mensagem",
            message="Conteúdo recebido.",
        )
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("interactions:contact-action", args=(contact.pk,)),
            {"action": "report"},
        )
        self.assertRedirects(response, reverse("interactions:contacts"))
        contact.refresh_from_db()
        self.assertEqual(contact.status, ContactRequest.Status.REPORTED)

    def test_duplicate_open_report_is_rejected(self):
        self.client.force_login(self.user)
        url = reverse("interactions:report", args=(self.profile.slug,))
        self.client.post(url, {"reason": "fraud", "description": "Informação suspeita."})

        response = self.client.post(url, {"reason": "false_data", "description": "Repetida."})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "denúncia activa")
        self.assertEqual(Report.objects.count(), 1)

    def test_notification_can_be_marked_as_read_only_by_owner(self):
        notification = Notification.objects.create(user=self.user, type="test", title="Teste")
        self.client.force_login(self.user)
        response = self.client.post(reverse("interactions:notification-read", args=(notification.pk,)))

        self.assertRedirects(response, reverse("interactions:notifications"))
        notification.refresh_from_db()
        self.assertIsNotNone(notification.read_at)

    def test_favorite_update_saves_status_notes_and_tags(self):
        favorite = Favorite.objects.create(user=self.user, profile=self.profile)
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("interactions:favorite-update", args=(favorite.pk,)),
            {"status": "interview", "notes": "Boa entrevista", "tags": "civil, senior"},
        )

        self.assertRedirects(response, reverse("interactions:favorites"))
        favorite.refresh_from_db()
        self.assertEqual(favorite.status, Favorite.Status.INTERVIEW)
        self.assertEqual(favorite.notes, "Boa entrevista")
        self.assertEqual(set(favorite.tags.values_list("name", flat=True)), {"civil", "senior"})

    def test_favorite_update_rejects_an_individual_tag_longer_than_eighty_characters_without_partial_update(self):
        favorite = Favorite.objects.create(
            user=self.user,
            profile=self.profile,
            status=Favorite.Status.SAVED,
            notes="Nota original",
        )
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("interactions:favorite-update", args=(favorite.pk,)),
            {"status": "interview", "notes": "Nota alterada", "tags": "a" * 81},
            follow=True,
        )

        self.assertContains(response, "N\u00e3o foi poss\u00edvel actualizar o favorito.")
        favorite.refresh_from_db()
        self.assertEqual(favorite.status, Favorite.Status.SAVED)
        self.assertEqual(favorite.notes, "Nota original")

    def test_favorite_update_rejects_tag_that_exceeds_limit_after_casefold_without_partial_update(self):
        favorite = Favorite.objects.create(
            user=self.user,
            profile=self.profile,
            status=Favorite.Status.SAVED,
            notes="Nota original",
        )
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("interactions:favorite-update", args=(favorite.pk,)),
            {"status": "interview", "notes": "Nota alterada", "tags": "ß" * 80},
            follow=True,
        )

        self.assertContains(response, "Não foi possível actualizar o favorito.")
        favorite.refresh_from_db()
        self.assertEqual(favorite.status, Favorite.Status.SAVED)
        self.assertEqual(favorite.notes, "Nota original")
        self.assertFalse(RecruitmentTag.objects.filter(user=self.user).exists())

    def test_favorite_add_is_idempotent_and_preserves_existing_shortlist_metadata(self):
        favorite = Favorite.objects.create(
            user=self.user,
            profile=self.profile,
            status=Favorite.Status.INTERVIEW,
            notes="Preparar proposta",
        )
        tag = RecruitmentTag.objects.create(user=self.user, name="Prioridade")
        favorite.tags.add(tag)
        self.client.force_login(self.user)

        response = self.client.post(f"/interacoes/favoritos/{self.profile.slug}/adicionar/")

        self.assertEqual(response.status_code, 302)
        favorite.refresh_from_db()
        self.assertEqual(favorite.status, Favorite.Status.INTERVIEW)
        self.assertEqual(favorite.notes, "Preparar proposta")
        self.assertEqual(list(favorite.tags.values_list("name", flat=True)), ["Prioridade"])

    def test_favorite_update_returns_404_for_another_users_favorite(self):
        other_favorite = Favorite.objects.create(user=self.other_user, profile=self.profile)
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("interactions:favorite-update", args=(other_favorite.pk,)), {"status": "interview"}
        )

        self.assertEqual(response.status_code, 404)

    def test_new_recruitment_routes_redirect_anonymous_users_to_login(self):
        favorite = Favorite.objects.create(user=self.user, profile=self.profile)
        saved_search = SavedSearch.objects.create(user=self.user, name="Engenharia", query_params={"q": "engenheiro"})
        urls = (
            reverse("interactions:favorites"),
            reverse("interactions:favorite-update", args=(favorite.pk,)),
            reverse("interactions:saved-search-create"),
            reverse("interactions:saved-search-run", args=(saved_search.pk,)),
            reverse("interactions:saved-search-delete", args=(saved_search.pk,)),
            reverse("interactions:compare"),
            reverse("interactions:shortlist-export"),
        )

        for url in urls:
            response = self.client.get(url)
            self.assertRedirects(response, f"{reverse('accounts:login')}?next={url}")

    def test_saved_search_create_cleans_params_and_redirects_to_search(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("interactions:saved-search-create"),
            {"name": "Engenharia", "q": "engenheiro", "experience": "5", "unsafe": "x"},
        )

        self.assertRedirects(response, reverse("search") + "?q=engenheiro&experience=5")
        self.assertEqual(
            SavedSearch.objects.get(user=self.user).query_params, {"q": "engenheiro", "experience": "5"}
        )

    def test_saved_search_run_redirects_to_the_saved_query(self):
        saved = SavedSearch.objects.create(
            user=self.user, name="Engenharia", query_params={"q": "engenheiro", "experience": "5"}
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("interactions:saved-search-run", args=(saved.pk,)))

        self.assertRedirects(response, reverse("search") + "?q=engenheiro&experience=5")

    def test_saved_search_run_returns_404_for_another_users_search(self):
        saved = SavedSearch.objects.create(user=self.other_user, name="Privada", query_params={"q": "privada"})
        self.client.force_login(self.user)

        response = self.client.get(reverse("interactions:saved-search-run", args=(saved.pk,)))

        self.assertEqual(response.status_code, 404)

    def test_saved_search_delete_returns_404_for_another_users_search(self):
        saved = SavedSearch.objects.create(user=self.other_user, name="Privada", query_params={"q": "privada"})
        self.client.force_login(self.user)

        response = self.client.post(reverse("interactions:saved-search-delete", args=(saved.pk,)))

        self.assertEqual(response.status_code, 404)
        self.assertTrue(SavedSearch.objects.filter(pk=saved.pk).exists())

    def test_saved_search_delete_returns_to_dashboard_when_requested(self):
        saved = SavedSearch.objects.create(user=self.user, name="Engenharia", query_params={"q": "engenheiro"})
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("interactions:saved-search-delete", args=(saved.pk,)),
            {"next": reverse("accounts:dashboard")},
        )

        self.assertRedirects(response, reverse("accounts:dashboard"))
        self.assertFalse(SavedSearch.objects.filter(pk=saved.pk).exists())

    def test_saved_search_delete_rejects_external_next_url(self):
        saved = SavedSearch.objects.create(user=self.user, name="Engenharia", query_params={"q": "engenheiro"})
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("interactions:saved-search-delete", args=(saved.pk,)),
            {"next": "https://example.com/destino-externo"},
        )

        self.assertRedirects(response, reverse("interactions:favorites"))
        self.assertFalse(SavedSearch.objects.filter(pk=saved.pk).exists())

    def test_compare_shows_only_public_profile_data(self):
        self.profile.phone = "+351 912 345 678"
        self.profile.save(update_fields=("phone",))
        Favorite.objects.create(user=self.user, profile=self.profile)
        self.client.force_login(self.user)

        response = self.client.get(reverse("interactions:compare"), {"profiles": str(self.profile.pk)})

        self.assertContains(response, self.profile.public_display_name)
        self.assertNotContains(response, self.profile.phone)

    def test_compare_includes_public_profile_with_changes_pending(self):
        self.profile.status = Profile.Status.CHANGES_PENDING
        self.profile.published_snapshot = {"public_name": "Perfil aprovado"}
        self.profile.save(update_fields=("status", "published_snapshot"))
        Favorite.objects.create(user=self.user, profile=self.profile)
        self.client.force_login(self.user)

        response = self.client.get(reverse("interactions:compare"), {"profiles": str(self.profile.pk)})

        self.assertContains(response, "Perfil aprovado")

    def test_compare_hides_city_and_country_when_location_is_private(self):
        self.profile.location = "Quebo"
        self.profile.country = "Guiné-Bissau"
        self.profile.location_is_public = False
        self.profile.save(update_fields=("location", "country", "location_is_public"))
        Favorite.objects.create(user=self.user, profile=self.profile)
        self.client.force_login(self.user)

        response = self.client.get(reverse("interactions:compare"), {"profiles": str(self.profile.pk)})

        comparison_html = response.content.decode().split(
            '<div class="compare-table compare-table-pro">',
            1,
        )[1].split("</div>", 1)[0]
        self.assertNotIn("Quebo", comparison_html)
        self.assertNotIn("Guiné-Bissau", comparison_html)

    def test_compare_uses_published_snapshot_for_recruitment_details(self):
        self.profile.published_snapshot = {
            "public_name": "Profissional Público",
            "professional_title": "Engenheiro",
            "location_is_public": True,
            "location": "Bissau",
            "country": "Guiné-Bissau",
            "work_preference_label": "Remoto aprovado",
            "availability_label": "Disponível aprovado",
            "skills": [],
            "education": [{"qualification": "Licenciatura aprovada", "institution": "Universidade aprovada"}],
            "languages": [{"name": "Português aprovado", "level": "Fluente"}],
        }
        self.profile.work_preference = Profile.WorkPreference.ONSITE
        self.profile.availability = Profile.Availability.UNAVAILABLE
        self.profile.save(update_fields=("published_snapshot", "work_preference", "availability"))
        Education.objects.create(
            profile=self.profile,
            qualification="Formação pendente",
            institution="Instituição pendente",
        )
        ProfileLanguage.objects.create(
            profile=self.profile,
            name="Idioma pendente",
            level=ProfileLanguage.Level.BASIC,
        )
        Favorite.objects.create(user=self.user, profile=self.profile)
        self.client.force_login(self.user)

        response = self.client.get(reverse("interactions:compare"), {"profiles": str(self.profile.pk)})

        self.assertContains(response, "Remoto aprovado")
        self.assertContains(response, "Disponível aprovado")
        self.assertContains(response, "Licenciatura aprovada")
        self.assertContains(response, "Português aprovado")
        self.assertNotContains(response, "Presencial")
        self.assertNotContains(response, "Indisponível")
        self.assertNotContains(response, "Formação pendente")
        self.assertNotContains(response, "Idioma pendente")

    def test_search_shortlist_and_comparison_hide_current_values_missing_from_snapshot(self):
        self.profile.professional_title = "Titulo actual secreto"
        self.profile.location = "Cidade actual secreta"
        self.profile.country = "Pais actual secreto"
        self.profile.work_preference = Profile.WorkPreference.ONSITE
        self.profile.availability = Profile.Availability.UNAVAILABLE
        self.profile.published_snapshot = {"public_name": "Nome aprovado"}
        self.profile.save()
        self.profile.skills.add(
            Skill.objects.create(name="Competencia actual secreta", slug="competencia-actual-secreta")
        )
        Education.objects.create(
            profile=self.profile,
            qualification="Formacao actual secreta",
            institution="Instituicao actual secreta",
        )
        ProfileLanguage.objects.create(
            profile=self.profile,
            name="Idioma actual secreto",
            level=ProfileLanguage.Level.BASIC,
        )
        Favorite.objects.create(user=self.user, profile=self.profile)
        self.client.force_login(self.user)

        search_response = self.client.get(reverse("search"))
        search_by_secret_skill_response = self.client.get(reverse("search"), {"q": "competencia actual secreta"})
        shortlist_response = self.client.get(reverse("interactions:favorites"))
        comparison_response = self.client.get(reverse("interactions:compare"), {"profiles": str(self.profile.pk)})

        for response in (search_response, shortlist_response, comparison_response):
            self.assertContains(response, "Nome aprovado")
            self.assertNotContains(response, "Titulo actual secreto")
            self.assertNotContains(response, "Cidade actual secreta")
            self.assertNotContains(response, "Pais actual secreto")
        self.assertEqual(search_response.context["page_obj"].object_list[0].public_skill_names, [])
        self.assertNotContains(search_by_secret_skill_response, "Nome aprovado")
        self.assertNotContains(shortlist_response, "Competencia actual secreta")
        self.assertNotContains(comparison_response, "Competencia actual secreta")
        self.assertNotContains(comparison_response, "Presencial")
        self.assertNotContains(comparison_response, "Indisponível")
        self.assertNotContains(comparison_response, "Formacao actual secreta")
        self.assertNotContains(comparison_response, "Idioma actual secreto")

    def test_compare_ignores_profiles_outside_users_shortlist(self):
        other_owner = get_user_model().objects.create_user(email="outro-perfil@example.com", password="test-pass")
        other_profile = other_owner.profile
        other_profile.public_name = "Perfil de outra shortlist"
        other_profile.status = Profile.Status.APPROVED
        other_profile.is_public = True
        other_profile.save()
        Favorite.objects.create(user=self.other_user, profile=other_profile)
        self.client.force_login(self.user)

        response = self.client.get(reverse("interactions:compare"), {"profiles": str(other_profile.pk)})

        self.assertNotContains(response, other_profile.public_display_name)

    def test_shortlist_export_excludes_private_email(self):
        Favorite.objects.create(user=self.user, profile=self.profile)
        self.client.force_login(self.user)

        response = self.client.get(reverse("interactions:shortlist-export"))

        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        self.assertNotContains(response, self.profile.user.email)

    def test_shortlist_export_includes_public_profile_with_changes_pending(self):
        self.profile.status = Profile.Status.CHANGES_PENDING
        self.profile.published_snapshot = {"public_name": "Perfil aprovado"}
        self.profile.save(update_fields=("status", "published_snapshot"))
        Favorite.objects.create(user=self.user, profile=self.profile)
        self.client.force_login(self.user)

        response = self.client.get(reverse("interactions:shortlist-export"))

        self.assertContains(response, "Perfil aprovado")

    def test_shortlist_export_excludes_another_users_favorite(self):
        other_owner = get_user_model().objects.create_user(email="exportar-outro@example.com", password="test-pass")
        other_profile = other_owner.profile
        other_profile.public_name = "Perfil privado de outra shortlist"
        other_profile.status = Profile.Status.APPROVED
        other_profile.is_public = True
        other_profile.save()
        Favorite.objects.create(user=self.other_user, profile=other_profile, notes="Nota privada")
        self.client.force_login(self.user)

        response = self.client.get(reverse("interactions:shortlist-export"))

        self.assertNotContains(response, other_profile.public_display_name)
        self.assertNotContains(response, "Nota privada")

    def test_favorites_page_shows_recruiter_shortlist_workspace(self):
        Favorite.objects.create(user=self.user, profile=self.profile)
        self.client.force_login(self.user)

        response = self.client.get(reverse("interactions:favorites"))

        self.assertContains(response, "Shortlist")
        self.assertContains(response, "Estado do processo")
        self.assertContains(response, "Exportar CSV")
        self.assertContains(response, "Comparar seleccionados")
        self.assertContains(response, "shortlist-card-refined")

    def test_favorites_page_includes_public_profile_with_changes_pending(self):
        self.profile.status = Profile.Status.CHANGES_PENDING
        self.profile.published_snapshot = {"public_name": "Perfil aprovado"}
        self.profile.save(update_fields=("status", "published_snapshot"))
        Favorite.objects.create(user=self.user, profile=self.profile)
        self.client.force_login(self.user)

        response = self.client.get(reverse("interactions:favorites"))

        self.assertContains(response, "Perfil aprovado")

    def test_favorites_page_hides_tag_owned_by_another_recruiter(self):
        favorite = Favorite.objects.create(user=self.user, profile=self.profile)
        foreign_tag = RecruitmentTag.objects.create(user=self.other_user, name="Etiqueta alheia")
        favorite.tags.add(foreign_tag)
        self.client.force_login(self.user)

        response = self.client.get(reverse("interactions:favorites"))

        self.assertNotContains(response, "Etiqueta alheia")

    def test_shortlist_export_link_encodes_reserved_tag_and_export_keeps_filter(self):
        favorite = Favorite.objects.create(user=self.user, profile=self.profile)
        favorite.tags.add(RecruitmentTag.objects.create(user=self.user, name="R&D"))
        other_owner = get_user_model().objects.create_user(email="sem-etiqueta@example.com", password="test-pass")
        other_profile = other_owner.profile
        other_profile.public_name = "Perfil sem etiqueta"
        other_profile.status = Profile.Status.APPROVED
        other_profile.is_public = True
        other_profile.save()
        Favorite.objects.create(user=self.user, profile=other_profile)
        self.client.force_login(self.user)

        response = self.client.get(reverse("interactions:favorites"), {"tag": "R&D"})

        self.assertContains(response, "?tag=R%26D")
        export_response = self.client.get(reverse("interactions:shortlist-export"), {"tag": "R&D"})
        self.assertContains(export_response, self.profile.public_display_name)
        self.assertNotContains(export_response, other_profile.public_display_name)

    def test_authenticated_search_shows_saved_search_and_shortlist_actions(self):
        self.profile.professional_title = "Engenheiro civil"
        self.profile.save(update_fields=("professional_title",))
        Experience.objects.create(
            profile=self.profile,
            title="Engenheiro civil",
            organization="Empresa",
            start_date=timezone.now().date().replace(year=timezone.now().year - 5),
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("search"), {"q": "engenheiro", "experience": "5"})

        self.assertContains(response, "Guardar pesquisa")
        self.assertContains(response, "Adicionar a shortlist")

    def test_anonymous_search_redirects_to_login(self):
        self.profile.professional_title = "Engenheiro civil"
        self.profile.save(update_fields=("professional_title",))

        response = self.client.get(reverse("search"), {"q": "engenheiro"})

        self.assertRedirects(
            response,
            f'{reverse("accounts:login")}?next={reverse("search")}%3Fq%3Dengenheiro',
        )

    def test_dashboard_shows_saved_searches_and_shortlist(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("accounts:dashboard"))

        self.assertContains(response, "Pesquisas guardadas")
        self.assertContains(response, "Shortlist")
