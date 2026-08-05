from django.test import TestCase
from django.utils import translation

from interactions.models import Notification
from profiles.forms import ProfileForm


class InterfaceLocalizationTests(TestCase):
    def test_public_home_is_rendered_in_english(self):
        self.client.post("/i18n/setlang/", {"language": "en", "next": "/"})

        response = self.client.get("/")

        self.assertContains(response, "Guinea-Bissau’s professional network")
        self.assertContains(response, "Request membership")
        self.assertContains(response, "Contact and languages")
        self.assertContains(response, "All rights reserved.")

    def test_public_home_is_rendered_in_french(self):
        self.client.post("/i18n/setlang/", {"language": "fr", "next": "/"})

        response = self.client.get("/")

        self.assertContains(response, "Le réseau professionnel de Guinée-Bissau")
        self.assertContains(response, "Demander l’adhésion")
        self.assertContains(response, "Contact et langues")
        self.assertContains(response, "Tous droits réservés.")

    def test_profile_form_labels_and_help_text_follow_active_language(self):
        with translation.override("en"):
            form = ProfileForm()
            self.assertEqual(str(form.fields["public_name"].label), "Public name")
            self.assertIn("recruiters", str(form.fields["search_keywords"].help_text))

    def test_notification_title_follows_active_language(self):
        notification = Notification(type="new_contact", title="Novo pedido de contacto")

        with translation.override("fr"):
            self.assertEqual(str(notification.localized_title), "Nouvelle demande de contact")
