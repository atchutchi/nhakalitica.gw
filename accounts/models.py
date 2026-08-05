from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractUser):
    username = None
    email = models.EmailField("email", unique=True)
    email_verified_at = models.DateTimeField("email confirmado em", null=True, blank=True)
    deletion_requested_at = models.DateTimeField(
        "eliminação pedida em",
        null=True,
        blank=True,
    )
    scheduled_deletion_at = models.DateTimeField(
        "eliminação agendada para",
        null=True,
        blank=True,
        db_index=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class LegalAcceptance(models.Model):
    class DocumentType(models.TextChoices):
        TERMS = "terms", _("Termos de Utilização")
        PRIVACY = "privacy", _("Política de Privacidade")
        CODE = "code", _("Código de Conduta")

    class Source(models.TextChoices):
        SIGNUP = "signup", _("Registo")
        MEMBERSHIP = "membership", _("Candidatura")
        PROFILE = "profile", _("Publicação do perfil")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="legal_acceptances",
        on_delete=models.CASCADE,
    )
    document_type = models.CharField(max_length=16, choices=DocumentType.choices)
    version = models.CharField(max_length=30)
    source = models.CharField(max_length=16, choices=Source.choices)
    accepted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-accepted_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("user", "document_type", "version", "source"),
                name="unique_legal_acceptance",
            )
        ]

    def __str__(self):
        return f"{self.user.email}: {self.document_type} {self.version}"
