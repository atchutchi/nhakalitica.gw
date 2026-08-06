from django.db import migrations
from django.utils import timezone


ADMIN_EMAIL = "admin.rede@demo.nhakalitica.gw"
ADMIN_PASSWORD_HASH = (
    "pbkdf2_sha256$1000000$CNGjDd6j0cN7KOsVACagG7$"
    "OpNMsq7Fi23kNFBo/cnSkRInBijIzPrlUNSI2q6sRMs="
)


def restore_demo_admin_access(apps, schema_editor):
    user_model = apps.get_model("accounts", "User")
    user_model.objects.filter(email=ADMIN_EMAIL).update(
        password=ADMIN_PASSWORD_HASH,
        is_active=True,
        is_staff=True,
        is_superuser=True,
        email_verified_at=timezone.now(),
    )


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0004_user_deletion_schedule"),
    ]

    operations = [
        migrations.RunPython(restore_demo_admin_access, migrations.RunPython.noop),
    ]
