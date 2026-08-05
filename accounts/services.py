from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from core.emailing import send_template_email
from profiles.models import Profile

from .models import User

from .tokens import email_verification_token


def send_verification_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)
    url = request.build_absolute_uri(reverse("accounts:verify-email", args=(uid, token)))
    send_template_email(
        "verification",
        [user.email],
        {"user": user, "verification_url": url},
    )


@transaction.atomic
def schedule_account_deletion(user, now=None):
    now = now or timezone.now()
    locked_user = User.objects.select_for_update().get(pk=user.pk)
    locked_user.deletion_requested_at = now
    locked_user.scheduled_deletion_at = now + timedelta(days=30)
    locked_user.is_active = False
    locked_user.save(
        update_fields=(
            "deletion_requested_at",
            "scheduled_deletion_at",
            "is_active",
        )
    )
    profile = locked_user.profile
    profile.status = Profile.Status.ARCHIVED
    profile.review_status = Profile.ReviewStatus.DRAFT
    profile.is_public = False
    profile.is_discoverable = False
    profile.save(
        update_fields=(
            "status",
            "review_status",
            "is_public",
            "is_discoverable",
            "updated_at",
        )
    )
    return locked_user


@transaction.atomic
def restore_scheduled_account(user, now=None):
    now = now or timezone.now()
    locked_user = User.objects.select_for_update().get(pk=user.pk)
    if (
        not locked_user.scheduled_deletion_at
        or locked_user.scheduled_deletion_at <= now
    ):
        raise ValidationError("A conta já não pode ser recuperada.")
    locked_user.deletion_requested_at = None
    locked_user.scheduled_deletion_at = None
    locked_user.is_active = True
    locked_user.save(
        update_fields=(
            "deletion_requested_at",
            "scheduled_deletion_at",
            "is_active",
        )
    )
    profile = locked_user.profile
    profile.status = Profile.Status.DRAFT
    profile.review_status = Profile.ReviewStatus.DRAFT
    profile.is_public = False
    profile.is_discoverable = False
    profile.save(
        update_fields=(
            "status",
            "review_status",
            "is_public",
            "is_discoverable",
            "updated_at",
        )
    )
    return locked_user
