from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone


class Command(BaseCommand):
    help = "Elimina contas cujo prazo de recuperação de 30 dias terminou."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Lista os IDs elegíveis sem eliminar contas.",
        )

    def handle(self, *args, **options):
        user_model = get_user_model()
        eligible_ids = list(
            user_model.objects.filter(
                is_active=False,
                scheduled_deletion_at__lte=timezone.now(),
            )
            .order_by("pk")
            .values_list("pk", flat=True)
        )
        if options["dry_run"]:
            for user_id in eligible_ids:
                self.stdout.write(f"ID {user_id} elegível para eliminação")
            self.stdout.write(f"Simulação concluída: {len(eligible_ids)} conta(s).")
            return

        deleted_count = 0
        for user_id in eligible_ids:
            try:
                with transaction.atomic():
                    user = user_model.objects.select_for_update().get(
                        pk=user_id,
                        is_active=False,
                        scheduled_deletion_at__lte=timezone.now(),
                    )
                    user.delete()
                deleted_count += 1
            except user_model.DoesNotExist:
                continue
            except Exception as error:
                self.stderr.write(
                    f"Falha ao eliminar ID {user_id} ({error.__class__.__name__})"
                )
        self.stdout.write(f"Eliminação concluída: {deleted_count} conta(s).")
