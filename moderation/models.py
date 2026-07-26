from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class AuditLog(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="autor",
        related_name="audit_events",
        on_delete=models.SET_NULL,
        null=True,
    )
    action = models.CharField("ação", max_length=100, db_index=True)
    target_type = models.CharField("tipo de alvo", max_length=100, db_index=True)
    target_id = models.CharField("identificador do alvo", max_length=64, db_index=True)
    metadata = models.JSONField("contexto", default=dict, blank=True)
    created_at = models.DateTimeField("criado em", auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-created_at", "-id")
        verbose_name = "registo de auditoria"
        verbose_name_plural = "registos de auditoria"

    def __str__(self):
        return f"{self.action} em {self.target_type} {self.target_id}"

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError("Os registos de auditoria não podem ser alterados.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Os registos de auditoria não podem ser eliminados.")
