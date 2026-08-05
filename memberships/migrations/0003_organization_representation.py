from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("memberships", "0002_membership_accepts_code_of_conduct_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="membership",
            name="represents_organization",
            field=models.BooleanField(default=False, verbose_name="Representa uma organização"),
        ),
        migrations.AddField(
            model_name="membership",
            name="organization_name",
            field=models.CharField(blank=True, max_length=180, verbose_name="Nome da organização"),
        ),
        migrations.AddField(
            model_name="membership",
            name="organization_role",
            field=models.CharField(blank=True, max_length=180, verbose_name="Função na organização"),
        ),
        migrations.AddField(
            model_name="membership",
            name="organization_purpose",
            field=models.TextField(blank=True, verbose_name="Objectivo da organização na rede"),
        ),
    ]
