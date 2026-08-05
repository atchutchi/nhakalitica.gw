from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0012_repair_current_profile_import_encoding"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="show_organization_on_profile",
            field=models.BooleanField(default=False, verbose_name="mostrar organização no perfil"),
        ),
    ]
