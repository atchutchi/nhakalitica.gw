from uuid import uuid4

from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from taxonomy.models import Skill, Specialization


class Profile(models.Model):
    class ReviewStatus(models.TextChoices):
        DRAFT = "draft", _("Rascunho")
        READY = "ready", _("Pronto para revisão")
        UNDER_REVIEW = "under_review", _("Em revisão")
        CORRECTIONS_REQUIRED = "corrections_required", _("Correcções necessárias")
        APPROVED = "approved", _("Publicado")

    class Status(models.TextChoices):
        DRAFT = "draft", _("Rascunho")
        PENDING = "pending", _("Pendente")
        APPROVED = "approved", _("Aprovado")
        REJECTED = "rejected", _("Rejeitado")
        CHANGES_PENDING = "changes_pending", _("Alterações pendentes")
        SUSPENDED = "suspended", _("Suspenso")
        ARCHIVED = "archived", _("Arquivado")
        DELETED = "deleted", _("Eliminado")

    class Availability(models.TextChoices):
        AVAILABLE = "available", _("Disponível")
        OPEN = "open", _("Aberto a propostas")
        UNAVAILABLE = "unavailable", _("Indisponível")

    class WorkPreference(models.TextChoices):
        ONSITE = "onsite", _("Presencial")
        REMOTE = "remote", _("Remoto")
        HYBRID = "hybrid", _("Híbrido")

    class Seniority(models.TextChoices):
        ENTRY = "entry", _("Entrada")
        JUNIOR = "junior", _("Júnior")
        MID = "mid", _("Intermédio")
        SENIOR = "senior", _("Sénior")
        LEAD = "lead", _("Liderança")

    class ContactVisibility(models.TextChoices):
        FORM = "form", _("Apenas formulário")
        REGISTERED = "registered", _("Utilizadores registados")
        PUBLIC = "public", _("Público")
        HIDDEN = "hidden", _("Oculto")

    class CVVisibility(models.TextChoices):
        PUBLIC = "public", _("Público")
        MEMBERS = "members", _("Utilizadores registados")
        REQUEST = "request", _("Apenas mediante pedido")
        PRIVATE = "private", _("Privado")

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name="utilizador",
        related_name="profile",
        on_delete=models.CASCADE,
    )
    slug = models.SlugField("slug público", max_length=190, unique=True, null=True, blank=True, editable=False)
    public_name = models.CharField("nome público", max_length=160, blank=True)
    professional_title = models.CharField("título profissional", max_length=180, blank=True)
    bio = models.TextField("biografia", blank=True)
    target_roles = models.TextField(
        "funções alvo",
        blank=True,
        help_text="Cargos pelos quais queres ser encontrado. Ex.: Engenheiro civil, gestor de projectos, consultor técnico.",
    )
    search_keywords = models.TextField(
        "palavras-chave de pesquisa",
        blank=True,
        help_text="Termos que recrutadores podem usar. Ex.: obras, fiscalização, AutoCAD, procurement, RH.",
    )
    location = models.CharField("localização", max_length=160, blank=True)
    location_is_public = models.BooleanField("mostrar localização", default=True)
    country = models.CharField("país", max_length=100, default="Guiné-Bissau")
    phone = models.CharField("telefone", max_length=40, blank=True)
    whatsapp = models.CharField("WhatsApp", max_length=40, blank=True)
    website = models.URLField("website", blank=True)
    linkedin_url = models.URLField("LinkedIn", blank=True)
    availability = models.CharField(
        "disponibilidade",
        max_length=20,
        choices=Availability.choices,
        default=Availability.OPEN,
    )
    work_preference = models.CharField(
        "preferência de trabalho",
        max_length=20,
        choices=WorkPreference.choices,
        default=WorkPreference.HYBRID,
    )
    willing_to_relocate = models.BooleanField("disponível para mudança", default=False)
    years_experience = models.PositiveSmallIntegerField("anos de experiência", null=True, blank=True)
    seniority_level = models.CharField(
        "nível profissional",
        max_length=20,
        choices=Seniority.choices,
        blank=True,
    )
    contact_visibility = models.CharField(
        "visibilidade dos contactos",
        max_length=20,
        choices=ContactVisibility.choices,
        default=ContactVisibility.FORM,
    )
    photo = models.ImageField("fotografia", upload_to="profile_photos/%Y/%m/", blank=True)
    cv_file = models.FileField("currículo em PDF", upload_to="resumes/%Y/%m/", blank=True)
    cv_uploaded_at = models.DateTimeField("currículo atualizado em", null=True, blank=True)
    cv_visibility = models.CharField(
        "visibilidade do currículo",
        max_length=20,
        choices=CVVisibility.choices,
        default=CVVisibility.PRIVATE,
    )
    status = models.CharField(
        "estado",
        max_length=24,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )
    is_public = models.BooleanField("público", default=False, db_index=True)
    review_status = models.CharField(
        "estado da publicação",
        max_length=24,
        choices=ReviewStatus.choices,
        default=ReviewStatus.DRAFT,
        db_index=True,
    )
    is_discoverable = models.BooleanField(
        "visível na rede",
        default=False,
        db_index=True,
    )
    approved_at = models.DateTimeField("aprovado em", null=True, blank=True)
    reviewed_at = models.DateTimeField("revisto em", null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="revisto por",
        related_name="reviewed_profiles",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    review_note = models.TextField("nota de revisão", blank=True)
    published_snapshot = models.JSONField("versão pública", default=dict, blank=True)
    published_at = models.DateTimeField("versão pública em", null=True, blank=True)
    specializations = models.ManyToManyField(
        Specialization,
        verbose_name="especializações",
        related_name="profiles",
        blank=True,
    )
    skills = models.ManyToManyField(
        Skill,
        verbose_name="competências",
        related_name="profiles",
        blank=True,
    )
    consent_profile_public = models.BooleanField("consentimento para perfil público", default=False)
    consent_contact = models.BooleanField("consentimento para contacto", default=False)
    consent_marketing = models.BooleanField("consentimento de marketing", default=False)
    show_organization_on_profile = models.BooleanField(
        _("mostrar organização no perfil"),
        default=False,
    )
    accepted_terms_version = models.CharField("versão dos termos", max_length=30, blank=True)
    accepted_terms_at = models.DateTimeField("termos aceites em", null=True, blank=True)
    accepted_privacy_version = models.CharField("versão da privacidade", max_length=30, blank=True)
    accepted_privacy_at = models.DateTimeField("privacidade aceite em", null=True, blank=True)
    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "perfil profissional"
        verbose_name_plural = "perfis profissionais"
        ordering = ("public_name", "user__email")

    def __str__(self):
        return self.public_name or self.user.email

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.public_name or self.user.get_full_name() or self.user.email.split("@", 1)[0])
            self.slug = f"{base or 'profissional'}-{uuid4().hex[:8]}"
        return super().save(*args, **kwargs)

    def missing_required_sections(self):
        checks = (
            ("nome público", bool(self.public_name.strip())),
            ("título profissional", bool(self.professional_title.strip())),
            ("biografia", bool(self.bio.strip())),
            ("localização", bool(self.location.strip())),
            ("especialização", self.specializations.exists()),
            ("competência", self.skills.exists()),
            ("experiência", self.experiences.exists()),
            ("formação", self.education_entries.exists()),
            ("idioma", self.languages.exists()),
        )
        return [label for label, complete in checks if not complete]

    @property
    def completion_percentage(self):
        total = 9
        return round(((total - len(self.missing_required_sections())) / total) * 100)

    @property
    def can_submit(self):
        return not self.missing_required_sections()

    def is_visible_to(self, viewer):
        viewer_membership = getattr(viewer, "membership", None)
        owner_membership = getattr(self.user, "membership", None)
        return bool(
            viewer.is_authenticated
            and viewer_membership
            and viewer_membership.can_access_network
            and owner_membership
            and owner_membership.can_access_network
            and self.review_status == self.ReviewStatus.APPROVED
            and self.is_discoverable
        )

    def build_public_snapshot(self):
        payload = {
            "public_name": self.public_name,
            "professional_title": self.professional_title,
            "bio": self.bio,
            "target_roles": self.target_roles,
            "search_keywords": self.search_keywords,
            "location": self.location,
            "location_is_public": self.location_is_public,
            "country": self.country,
            "availability": self.availability,
            "availability_label": self.get_availability_display(),
            "work_preference": self.work_preference,
            "work_preference_label": self.get_work_preference_display(),
            "years_experience": self.years_experience,
            "seniority_level": self.seniority_level,
            "seniority_label": self.get_seniority_level_display() if self.seniority_level else "",
            "skills": list(self.skills.values_list("name", flat=True)),
            "specializations": list(self.specializations.values_list("name", flat=True)),
            "areas": list(self.specializations.values_list("area__name", flat=True).distinct()),
            "sectors": list(self.specializations.values_list("area__sector__name", flat=True).distinct()),
            "experiences": [
                {
                    "title": item.title,
                    "organization": item.organization,
                    "description": item.description,
                    "start_date": item.start_date.isoformat(),
                    "end_date": item.end_date.isoformat() if item.end_date else "",
                }
                for item in self.experiences.all()
            ],
            "education": [
                {
                    "qualification": item.qualification,
                    "institution": item.institution,
                    "field_of_study": item.field_of_study,
                }
                for item in self.education_entries.all()
            ],
            "certifications": [
                {"name": item.name, "issuer": item.issuer}
                for item in self.certifications.all()
            ],
            "languages": [
                {"name": item.name, "level": item.get_level_display()}
                for item in self.languages.all()
            ],
        }
        membership = getattr(self.user, "membership", None)
        if (
            self.show_organization_on_profile
            and membership
            and membership.can_access_network
            and membership.represents_organization
        ):
            payload["organization_name"] = membership.organization_name
            payload["organization_role"] = membership.organization_role
        return payload

    @property
    def public_payload(self):
        return self.published_snapshot or self.build_public_snapshot()

    @property
    def public_display_name(self):
        if self.published_snapshot:
            return self.public_payload.get("public_name", "")
        return self.public_name

    @property
    def public_professional_title(self):
        if self.published_snapshot:
            return self.public_payload.get("professional_title", "")
        return self.professional_title

    @property
    def public_location(self):
        if self.published_snapshot:
            if not self.public_payload.get("location_is_public", False):
                return ""
            return self.public_payload.get("location", "")
        if not self.location_is_public:
            return ""
        return self.location

    @property
    def public_country(self):
        if self.published_snapshot:
            if not self.public_payload.get("location_is_public", False):
                return ""
            return self.public_payload.get("country", "")
        if not self.location_is_public:
            return ""
        return self.country

    @property
    def public_skill_names(self):
        if self.published_snapshot:
            return self.public_payload.get("skills", [])
        return list(self.skills.values_list("name", flat=True))

    @property
    def demo_avatar_path(self):
        index = ((self.pk or 1) - 1) % 6 + 1
        return f"img/demo-avatars/avatar-{index}.webp"


class ProfileRevision(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendente"
        APPROVED = "approved", "Aprovada"
        REJECTED = "rejected", "Rejeitada"
        CANCELLED = "cancelled", "Cancelada"

    profile = models.ForeignKey(Profile, related_name="revisions", on_delete=models.CASCADE)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="submitted_profile_revisions", on_delete=models.CASCADE
    )
    payload = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    review_note = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="reviewed_profile_revisions",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-submitted_at", "-id")
        verbose_name = "revisão de perfil"
        verbose_name_plural = "revisões de perfil"

    def __str__(self):
        return f"Revisão de {self.profile} em {self.submitted_at:%d/%m/%Y}"


class Experience(models.Model):
    profile = models.ForeignKey(Profile, related_name="experiences", on_delete=models.CASCADE)
    title = models.CharField("cargo", max_length=180)
    organization = models.CharField("organização", max_length=180)
    location = models.CharField("localização", max_length=160, blank=True)
    description = models.TextField("descrição", blank=True)
    start_date = models.DateField("data de início")
    end_date = models.DateField("data de fim", null=True, blank=True)
    is_current = models.BooleanField("cargo atual", default=False)

    class Meta:
        ordering = ("-start_date", "-id")
        verbose_name = "experiência profissional"
        verbose_name_plural = "experiências profissionais"

    def __str__(self):
        return f"{self.title} em {self.organization}"


class Education(models.Model):
    profile = models.ForeignKey(Profile, related_name="education_entries", on_delete=models.CASCADE)
    institution = models.CharField("instituição", max_length=180)
    qualification = models.CharField("qualificação", max_length=180)
    field_of_study = models.CharField("área de estudo", max_length=180, blank=True)
    start_date = models.DateField("data de início", null=True, blank=True)
    end_date = models.DateField("data de fim", null=True, blank=True)
    description = models.TextField("descrição", blank=True)

    class Meta:
        ordering = ("-end_date", "-id")
        verbose_name = "formação"
        verbose_name_plural = "formações"

    def __str__(self):
        return f"{self.qualification}, {self.institution}"


class Certification(models.Model):
    profile = models.ForeignKey(Profile, related_name="certifications", on_delete=models.CASCADE)
    name = models.CharField("certificação", max_length=180)
    issuer = models.CharField("entidade emissora", max_length=180)
    issue_date = models.DateField("data de emissão", null=True, blank=True)
    expiry_date = models.DateField("data de validade", null=True, blank=True)
    credential_url = models.URLField("ligação da credencial", blank=True)

    class Meta:
        ordering = ("-issue_date", "name")
        verbose_name = "certificação"
        verbose_name_plural = "certificações"

    def __str__(self):
        return self.name


class ProfileLanguage(models.Model):
    class Level(models.TextChoices):
        BASIC = "basic", "Básico"
        INTERMEDIATE = "intermediate", "Intermédio"
        ADVANCED = "advanced", "Avançado"
        FLUENT = "fluent", "Fluente"
        NATIVE = "native", "Nativo"

    profile = models.ForeignKey(Profile, related_name="languages", on_delete=models.CASCADE)
    name = models.CharField("idioma", max_length=100)
    level = models.CharField("nível", max_length=20, choices=Level.choices)

    class Meta:
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(fields=("profile", "name"), name="unique_profile_language")
        ]
        verbose_name = "idioma"
        verbose_name_plural = "idiomas"

    def __str__(self):
        return f"{self.name}, {self.get_level_display()}"
