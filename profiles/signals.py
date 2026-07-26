from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import User

from .models import Profile


@receiver(post_save, sender=User)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    if created:
        public_name = f"{instance.first_name} {instance.last_name}".strip()
        Profile.objects.create(user=instance, public_name=public_name)
