from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from profiles.models import Profile


class UserProfileRelation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Favorite(UserProfileRelation):
    class Status(models.TextChoices):
        SAVED = "saved", _("Guardado")
        TO_CONTACT = "to_contact", _("Para contactar")
        CONTACTED = "contacted", _("Contactado")
        INTERVIEW = "interview", _("Entrevista")
        OFFER = "offer", _("Proposta")
        HIRED = "hired", _("Contratado")
        ARCHIVED = "archived", _("Arquivado")

    status = models.CharField(max_length=24, choices=Status.choices, default=Status.SAVED, db_index=True)
    notes = models.TextField(blank=True, max_length=3000)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField("RecruitmentTag", related_name="favorites", blank=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [models.UniqueConstraint(fields=("user", "profile"), name="unique_favorite")]
        verbose_name = "favorito"
        verbose_name_plural = "favoritos"


class RecruitmentTagManager(models.Manager):
    def normalise_name(self, name: str) -> str:
        return " ".join(name.split()).casefold()


class RecruitmentTag(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="recruitment_tags", on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    normalized_name = models.CharField(max_length=80, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = RecruitmentTagManager()

    def clean(self):
        self.name = " ".join(self.name.split())
        self.normalized_name = type(self).objects.normalise_name(self.name)
        max_length = self._meta.get_field("name").max_length
        if len(self.name) > max_length or len(self.normalized_name) > max_length:
            raise ValidationError({"name": _("Etiqueta com mais de %(max_length)s caracteres.") % {"max_length": max_length}})

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ("name",)
        constraints = [models.UniqueConstraint(fields=("user", "normalized_name"), name="unique_recruitment_tag")]
        verbose_name = "etiqueta de recrutamento"
        verbose_name_plural = "etiquetas de recrutamento"


class SavedSearch(models.Model):
    QUERY_PARAMS = frozenset(
        {
            "q",
            "sector",
            "area",
            "specialization",
            "skill",
            "location",
            "country",
            "availability",
            "work_preference",
            "seniority",
            "language",
            "experience",
            "cv",
            "order",
        }
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="saved_searches", on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    query_params = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def allowed_query_params(cls) -> set[str]:
        return set(cls.QUERY_PARAMS)

    def clean(self):
        if not isinstance(self.query_params, dict):
            raise ValidationError({"query_params": _("Os parâmetros da pesquisa têm de ser um objeto JSON.")})

        self.query_params = {
            key: value
            for key, value in self.query_params.items()
            if key in self.allowed_query_params()
            and value is not None
            and (not isinstance(value, str) or value.strip())
        }

    class Meta:
        ordering = ("-updated_at",)
        verbose_name = "pesquisa guardada"
        verbose_name_plural = "pesquisas guardadas"


class ProfileLike(UserProfileRelation):
    class Meta:
        ordering = ("-created_at",)
        constraints = [models.UniqueConstraint(fields=("user", "profile"), name="unique_profile_like")]
        verbose_name = "gosto"
        verbose_name_plural = "gostos"


class ContactRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pendente")
        ACCEPTED = "accepted", _("Aceite")
        DECLINED = "declined", _("Recusado")
        BLOCKED = "blocked", _("Bloqueado")
        REPORTED = "reported", _("Denunciado")

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="sent_contact_requests", on_delete=models.CASCADE
    )
    profile = models.ForeignKey(Profile, related_name="contact_requests", on_delete=models.CASCADE)
    subject = models.CharField("assunto", max_length=180)
    message = models.TextField("mensagem", max_length=3000)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    sender_ip_hash = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "pedido de contacto"
        verbose_name_plural = "pedidos de contacto"


class Report(models.Model):
    class Reason(models.TextChoices):
        FALSE_DATA = "false_data", _("Informação falsa")
        FRAUD = "fraud", _("Suspeita de fraude")
        IMPERSONATION = "impersonation", _("Dados de outra pessoa")
        PROHIBITED = "prohibited", _("Conteúdo proibido")
        SPAM = "spam", _("Conteúdo promocional ou spam")
        OTHER = "other", _("Outro motivo")

    class Status(models.TextChoices):
        OPEN = "open", _("Aberta")
        REVIEWING = "reviewing", _("Em análise")
        RESOLVED = "resolved", _("Resolvida")
        DISMISSED = "dismissed", _("Arquivada")

    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="reports", on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, related_name="reports", on_delete=models.CASCADE)
    reason = models.CharField(max_length=30, choices=Reason.choices)
    description = models.TextField(blank=True, max_length=2000)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN, db_index=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="assigned_reports",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    resolution_note = models.TextField(blank=True, max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("reporter", "profile"),
                condition=Q(status__in=("open", "reviewing")),
                name="unique_active_profile_report",
            )
        ]
        verbose_name = "denúncia"
        verbose_name_plural = "denúncias"


class Notification(models.Model):
    TITLES = {
        "new_contact": _("Novo pedido de contacto"),
        "new_report": _("Nova denúncia de perfil"),
        "contact_reported": _("Contacto denunciado"),
        "profile_submitted": _("Novo perfil para revisão"),
        "profile_approve": _("Perfil aprovado"),
        "profile_reject": _("Perfil rejeitado"),
        "profile_request_changes": _("Correcções solicitadas"),
        "profile_suspend": _("Conta suspensa"),
        "profile_restore": _("Conta restaurada"),
        "membership_under_review": _("Candidatura em análise"),
        "membership_corrections_required": _("Correcções solicitadas"),
        "membership_approved": _("Adesão aprovada"),
        "membership_refused": _("Decisão sobre a adesão"),
        "membership_suspended": _("Adesão suspensa"),
        "report_resolved": _("Denúncia analisada"),
    }
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="notifications", on_delete=models.CASCADE)
    type = models.CharField("tipo", max_length=60, db_index=True)
    title = models.CharField("título", max_length=180)
    body = models.TextField("conteúdo", blank=True, max_length=1000)
    link = models.CharField("destino", max_length=300, blank=True)
    read_at = models.DateTimeField("lida em", null=True, blank=True, db_index=True)
    created_at = models.DateTimeField("criada em", auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "notificação"
        verbose_name_plural = "notificações"

    @property
    def localized_title(self):
        return self.TITLES.get(self.type, self.title)
