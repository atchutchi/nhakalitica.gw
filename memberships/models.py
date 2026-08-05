from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Membership(models.Model):
    class Type(models.TextChoices):
        EFFECTIVE = "effective", _("Efectivo")
        OBSERVER = "observer", _("Observador")

    class Relationship(models.TextChoices):
        CITIZEN = "citizen", _("Cidadão da Guiné-Bissau")
        DIASPORA = "diaspora", _("Descendente da diáspora")
        RELEVANT_LINK = "relevant_link", _("Ligação relevante")

    class Status(models.TextChoices):
        DRAFT = "draft", _("Rascunho")
        SUBMITTED = "submitted", _("Submetida")
        UNDER_REVIEW = "under_review", _("Em análise")
        CORRECTIONS_REQUIRED = "corrections_required", _("Correcções necessárias")
        APPROVED = "approved", _("Aprovada")
        REFUSED = "refused", _("Recusada")
        SUSPENDED = "suspended", _("Suspensa")

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="membership",
    )
    member_type = models.CharField(max_length=16, choices=Type.choices, blank=True)
    relationship = models.CharField(
        max_length=20,
        choices=Relationship.choices,
        blank=True,
    )
    relationship_note = models.TextField(blank=True)
    motivation = models.TextField(blank=True)
    represents_organization = models.BooleanField(
        _("Representa uma organização"),
        default=False,
    )
    organization_name = models.CharField(_("Nome da organização"), max_length=180, blank=True)
    organization_role = models.CharField(_("Função na organização"), max_length=180, blank=True)
    organization_purpose = models.TextField(_("Objectivo da organização na rede"), blank=True)
    accepts_code_of_conduct = models.BooleanField(
        _("Aceita o código de conduta"),
        default=False,
    )
    accepts_privacy = models.BooleanField(
        _("Aceita a política de privacidade"),
        default=False,
    )
    confirms_truth = models.BooleanField(
        _("Confirma a veracidade da candidatura"),
        default=False,
    )
    status = models.CharField(
        max_length=24,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at",)

    @property
    def can_access_network(self):
        return self.status == self.Status.APPROVED

    @property
    def can_edit_application(self):
        return self.status in {
            self.Status.DRAFT,
            self.Status.CORRECTIONS_REQUIRED,
        }

    def __str__(self):
        return f"{self.user.email} · {self.get_status_display()}"


class MembershipDecision(models.Model):
    membership = models.ForeignKey(
        Membership,
        on_delete=models.CASCADE,
        related_name="decisions",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="membership_decisions",
    )
    from_status = models.CharField(max_length=24, choices=Membership.Status.choices)
    to_status = models.CharField(max_length=24, choices=Membership.Status.choices)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.membership.user.email}: {self.from_status} → {self.to_status}"
