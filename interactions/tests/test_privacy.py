from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from interactions.models import ContactRequest, Favorite
from interactions.services import create_contact, toggle_favorite
from memberships.models import Membership
from profiles.models import Profile


class InteractionPrivacyTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.sender = user_model.objects.create_user(
            email="sender@example.com",
            password="Segura2026!",
        )
        self.sender.email_verified_at = timezone.now()
        self.sender.save(update_fields=("email_verified_at",))
        self.owner = user_model.objects.create_user(
            email="owner@example.com",
            password="Segura2026!",
        )
        self.candidate = user_model.objects.create_user(
            email="candidate@example.com",
            password="Segura2026!",
        )
        for user in (self.sender, self.owner):
            user.membership.status = Membership.Status.APPROVED
            user.membership.save(update_fields=("status",))

        self.profile = self.owner.profile
        self.profile.public_name = "Profissional Aprovada"
        self.profile.review_status = Profile.ReviewStatus.APPROVED
        self.profile.is_discoverable = True
        self.profile.consent_contact = True
        self.profile.save()

    def test_candidate_cannot_favorite_profile(self):
        self.client.force_login(self.candidate)

        response = self.client.post(
            reverse("interactions:favorite-add", args=(self.profile.slug,)),
        )

        self.assertRedirects(response, reverse("memberships:dashboard"))
        self.assertFalse(Favorite.objects.exists())

    def test_direct_service_rejects_candidate(self):
        with self.assertRaises(PermissionDenied):
            toggle_favorite(self.candidate, self.profile)

    def test_suspended_profile_owner_cannot_receive_interactions(self):
        self.owner.membership.status = Membership.Status.SUSPENDED
        self.owner.membership.save(update_fields=("status",))

        with self.assertRaises(PermissionDenied):
            toggle_favorite(self.sender, self.profile)

    def test_contact_request_starts_pending_without_exposing_email(self):
        contact = create_contact(
            self.sender,
            self.profile,
            "Colaboração",
            "Gostaria de apresentar uma oportunidade profissional.",
        )

        self.assertEqual(contact.status, ContactRequest.Status.PENDING)
        self.assertNotIn(self.profile.user.email, contact.message)
        self.assertNotIn(self.sender.email, contact.message)

    def test_contact_email_is_hidden_until_recipient_accepts(self):
        contact = create_contact(
            self.sender,
            self.profile,
            "Colaboração",
            "Gostaria de apresentar uma oportunidade profissional.",
        )
        self.client.force_login(self.owner)

        pending = self.client.get(reverse("interactions:contacts"))
        self.assertNotContains(pending, self.sender.email)

        response = self.client.post(
            reverse("interactions:contact-action", args=(contact.pk,)),
            {"action": "accept"},
        )
        self.assertRedirects(response, reverse("interactions:contacts"))
        accepted = self.client.get(reverse("interactions:contacts"))
        self.assertContains(accepted, self.sender.email)

    def test_suspension_removes_existing_favorite_from_private_lists(self):
        favorite = Favorite.objects.create(user=self.sender, profile=self.profile)
        self.owner.membership.status = Membership.Status.SUSPENDED
        self.owner.membership.save(update_fields=("status",))
        self.client.force_login(self.sender)

        response = self.client.get(reverse("interactions:favorites"))

        self.assertNotContains(response, self.profile.public_name)
        self.assertTrue(Favorite.objects.filter(pk=favorite.pk).exists())
