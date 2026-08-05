from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_legal_acceptance"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="deletion_requested_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="eliminação pedida em"),
        ),
        migrations.AddField(
            model_name="user",
            name="scheduled_deletion_at",
            field=models.DateTimeField(
                blank=True,
                db_index=True,
                null=True,
                verbose_name="eliminação agendada para",
            ),
        ),
    ]
