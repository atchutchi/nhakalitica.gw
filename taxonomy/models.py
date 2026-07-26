from django.db import models


class NamedActiveModel(models.Model):
    name = models.CharField("nome", max_length=160)
    slug = models.SlugField("slug", max_length=180, unique=True)
    is_active = models.BooleanField("ativo", default=True)
    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        abstract = True
        ordering = ("name",)

    def __str__(self):
        return self.name


class Sector(NamedActiveModel):
    class Meta(NamedActiveModel.Meta):
        verbose_name = "setor"
        verbose_name_plural = "setores"


class Area(NamedActiveModel):
    sector = models.ForeignKey(
        Sector,
        verbose_name="setor",
        related_name="areas",
        on_delete=models.PROTECT,
    )

    class Meta(NamedActiveModel.Meta):
        verbose_name = "área"
        verbose_name_plural = "áreas"


class Specialization(NamedActiveModel):
    area = models.ForeignKey(
        Area,
        verbose_name="área",
        related_name="specializations",
        on_delete=models.PROTECT,
    )

    class Meta(NamedActiveModel.Meta):
        verbose_name = "especialização"
        verbose_name_plural = "especializações"


class Skill(NamedActiveModel):
    specializations = models.ManyToManyField(
        Specialization,
        verbose_name="especializações",
        related_name="skills",
        blank=True,
    )

    class Meta(NamedActiveModel.Meta):
        verbose_name = "competência"
        verbose_name_plural = "competências"
