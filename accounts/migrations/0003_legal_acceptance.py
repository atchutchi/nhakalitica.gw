from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_user_email_verified_at"),
    ]

    operations = [
        migrations.CreateModel(
            name="LegalAcceptance",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "document_type",
                    models.CharField(
                        choices=[
                            ("terms", "Termos de Utilização"),
                            ("privacy", "Política de Privacidade"),
                            ("code", "Código de Conduta"),
                        ],
                        max_length=16,
                    ),
                ),
                ("version", models.CharField(max_length=30)),
                (
                    "source",
                    models.CharField(
                        choices=[
                            ("signup", "Registo"),
                            ("membership", "Candidatura"),
                            ("profile", "Publicação do perfil"),
                        ],
                        max_length=16,
                    ),
                ),
                ("accepted_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="legal_acceptances",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ("-accepted_at",)},
        ),
        migrations.AddConstraint(
            model_name="legalacceptance",
            constraint=models.UniqueConstraint(
                fields=("user", "document_type", "version", "source"),
                name="unique_legal_acceptance",
            ),
        ),
    ]
