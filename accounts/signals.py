from django.db.models.signals import post_save
from django.dispatch import receiver

from memberships.models import Membership
from profiles.models import Profile

from .models import User


@receiver(post_save, sender=User)
def create_workspace_for_new_user(sender, instance, created, **kwargs):
    if created:
        public_name = f"{instance.first_name} {instance.last_name}".strip()
        Profile.objects.get_or_create(
            user=instance,
            defaults={"public_name": public_name},
        )
        Membership.objects.get_or_create(user=instance)
