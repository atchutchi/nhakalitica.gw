from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("profiles", "0008_normalize_existing_profile_text"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="target_roles",
            field=models.TextField(
                blank=True,
                help_text="Cargos pelos quais queres ser encontrado. Ex.: Engenheiro civil, gestor de projectos, consultor técnico.",
                verbose_name="funções alvo",
            ),
        ),
        migrations.AddField(
            model_name="profile",
            name="search_keywords",
            field=models.TextField(
                blank=True,
                help_text="Termos que recrutadores podem usar. Ex.: obras, fiscalização, AutoCAD, procurement, RH.",
                verbose_name="palavras-chave de pesquisa",
            ),
        ),
        migrations.AddField(
            model_name="profile",
            name="years_experience",
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="anos de experiência"),
        ),
        migrations.AddField(
            model_name="profile",
            name="seniority_level",
            field=models.CharField(
                blank=True,
                choices=[
                    ("entry", "Entrada"),
                    ("junior", "Júnior"),
                    ("mid", "Intermédio"),
                    ("senior", "Sénior"),
                    ("lead", "Liderança"),
                ],
                max_length=20,
                verbose_name="nível profissional",
            ),
        ),
    ]
